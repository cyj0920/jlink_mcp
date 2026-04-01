"""Connection Management Tool Functions / 连接管理工具函数."""

from typing import List, Dict, Any

from ..config_manager import config_manager
from ..jlink_manager import jlink_manager
from ..models.device import TargetInterface
from ..utils import logger


DEVICE_FIELDS = (
    "serial_number",
    "product_name",
    "firmware_version",
    "hardware_version",
    "connection_type",
)

STATUS_FIELDS = (
    "connected",
    "device_serial",
    "target_interface",
    "target_voltage",
    "target_connected",
    "firmware_version",
    "connection_mode",
    "connection_strategy",
    "requested_chip_name",
    "connected_chip_name",
)


def _serialize_object(obj: Any, fields: tuple[str, ...]) -> Dict[str, Any]:
    """Serialize pydantic model or mock object / 序列化 Pydantic 模型或 Mock 对象."""
    model_dump = getattr(obj, "model_dump", None)
    if callable(model_dump):
        dumped = model_dump()
        if isinstance(dumped, dict):
            return dumped
    return {field: getattr(obj, field, None) for field in fields}


def list_jlink_devices() -> List[Dict[str, Any]]:
    """列出所有连接的 JLink 设备.

    返回系统中所有已连接的 JLink 调试器列表。
    每个设备包含序列号、产品名称和连接类型。

    Returns:
        设备信息列表，每个设备包含:
        - serial_number: 设备序列号
        - product_name: 产品名称
        - firmware_version: 固件版本
        - connection_type: 连接类型（USB/ETH）
    """
    devices = jlink_manager.enumerate_devices()
    return [_serialize_object(device, DEVICE_FIELDS) for device in devices]


def connect_device(serial_number: str | None = None, interface: str | None = None, chip_name: str | None = None) -> Dict[str, Any]:
    """连接到 JLink 设备.

    连接到指定的 JLink 调试器。如果不指定序列号，则连接第一个可用设备。
    连接成功后，可以执行其他操作如读写内存、控制调试等。

    Args:
        serial_number: 设备序列号（可选，None 则连接第一个设备）
        interface: 目标接口类型，支持 "SWD" 或 "JTAG"（可选，默认从配置读取）
        chip_name: 目标芯片名称（可选，支持缩写自动匹配，如 FC7300F4MDD）

    Returns:
        连接结果，包含:
        - success: 是否成功
        - serial_number: 连接的设备序列号
        - message: 状态信息
    """
    try:
        if interface is None:
            config = config_manager.get_config()
            interface = config.default_interface
            logger.debug(f"使用配置的默认接口: {interface}")

        interface_enum = TargetInterface(interface.upper())
        jlink_manager.connect(serial_number, interface_enum, chip_name)
        status = jlink_manager.get_connection_status()
        status_data = _serialize_object(status, STATUS_FIELDS)

        logger.info(f"成功连接到设备: {status_data['device_serial']}")
        return {
            "success": True,
            "serial_number": status_data["device_serial"],
            "mode": status_data["connection_mode"],
            "strategy": status_data["connection_strategy"],
            "requested_chip_name": status_data["requested_chip_name"],
            "connected_chip_name": status_data["connected_chip_name"],
            "message": (
                f"成功连接到设备 {status_data['device_serial']}，接口: {interface}，"
                f"模式: {status_data['connection_mode']}"
            ),
        }
    except Exception as e:
        logger.error(f"连接失败: {e}")
        from ..exceptions import JLinkErrorCode

        error_msg = str(e)
        code = JLinkErrorCode.CONNECTION_FAILED

        if "unsupported device" in error_msg.lower() or "not found" in error_msg.lower():
            code = JLinkErrorCode.DEVICE_NOT_FOUND
            from ..device_patch_manager import device_patch_manager
            suggestion = "请检查设备连接或尝试其他芯片名称"
            if chip_name:
                suggestions = device_patch_manager.get_device_name_suggestions(chip_name)
                suggestion = suggestions
        elif chip_name:
            suggestion = (
                "请检查芯片名称、接口类型和目标供电状态；"
                "如果只需要核心级调试，可尝试启用 JLINK_GENERIC_CORE_FALLBACK"
            )
        else:
            suggestion = "请检查设备连接状态，尝试重新插拔设备"

        return {
            "success": False,
            "serial_number": None,
            "error": {
                "code": code.value[0],
                "description": code.value[1],
                "detail": error_msg,
                "suggestion": suggestion,
            },
        }


def disconnect_device() -> Dict[str, Any]:
    """断开 JLink 设备连接.

    断开当前活动的 JLink 连接，释放设备资源。
    建议在不使用时调用此函数。

    Returns:
        断开结果，包含:
        - success: 是否成功
        - message: 状态信息
    """
    try:
        jlink_manager.disconnect()
        logger.info("设备已断开连接")
        return {
            "success": True,
            "message": "设备已断开连接"
        }
    except Exception as e:
        logger.error(f"断开连接失败: {e}")
        from ..exceptions import JLinkErrorCode
        return {
            "success": False,
            "error": {
                "code": JLinkErrorCode.CONNECTION_LOST.value[0],
                "description": JLinkErrorCode.CONNECTION_LOST.value[1],
                "detail": str(e),
                "suggestion": JLinkErrorCode.CONNECTION_LOST.value[2]
            }
        }


def get_connection_status() -> Dict[str, Any]:
    """获取当前连接状态.

    查询 JLink 连接状态、目标芯片连接状态、电压等信息。

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - data: 连接状态数据
            - connected: 是否已连接
            - device_serial: 设备序列号
            - target_interface: 目标接口类型
            - target_voltage: 目标电压（V）
            - target_connected: 目标芯片是否已连接
            - firmware_version: JLink 固件版本
    """
    try:
        status = jlink_manager.get_connection_status()
        return {
            "success": True,
            "data": _serialize_object(status, STATUS_FIELDS),
            "message": "获取连接状态成功"
        }
    except Exception as e:
        logger.error(f"获取连接状态失败: {e}")
        from ..exceptions import JLinkErrorCode
        return {
            "success": False,
            "data": None,
            "error": {
                "code": JLinkErrorCode.UNKNOWN_ERROR.value[0],
                "description": str(e),
                "suggestion": "请检查 JLink 设备连接状态"
            }
        }


def match_chip_name(chip_name: str) -> Dict[str, Any]:
    """智能匹配芯片名称.

    将简化的芯片名称（如 FC7300F4MDD）匹配到完整的芯片名称
    （如 FC7300F4MDDxXxxxT1C）。

    支持多种匹配模式：
    - 精确匹配：FC7300F4MDDxXxxxT1C -> FC7300F4MDDxXxxxT1C
    - 前缀匹配：FC7300F4MDD -> FC7300F4MDDxXxxxT1C
    - 包含匹配：FC7300F4MDDS -> FC7300F4MDSxXxxxT1C
    - 模糊匹配：FC7300F4MDDxT1C -> FC7300F4MDDxXxxxT1C

    Args:
        chip_name: 芯片名称（可以是简化名称或完整名称）

    Returns:
        匹配结果，包含:
        - success: 是否找到匹配
        - input: 输入的芯片名称
        - matched: 匹配到的完整名称（如果有）
        - all_matches: 所有匹配的设备列表
        - suggestion: 建议信息
    """
    from ..device_patch_manager import device_patch_manager

    if not chip_name or not chip_name.strip():
        return {
            "success": False,
            "input": chip_name,
            "matched": None,
            "all_matches": [],
            "suggestion": "芯片名称不能为空"
        }

    chip_name = chip_name.strip()
    match_result = device_patch_manager.match_device_name(chip_name)

    if not match_result:
        all_matches = device_patch_manager.find_similar_devices(chip_name, limit=10)
        suggestion = device_patch_manager.get_device_name_suggestions(chip_name)
        logger.warning(f"芯片名称未找到匹配: '{chip_name}'")
        return {
            "success": False,
            "input": chip_name,
            "matched": None,
            "all_matches": all_matches,
            "suggestion": suggestion
        }

    matched, patch = match_result
    all_matches = device_patch_manager.find_similar_devices(chip_name, limit=10)

    logger.info(f"芯片名称匹配成功: '{chip_name}' -> '{matched}' (补丁: {patch.vendor_name})")
    return {
        "success": True,
        "input": chip_name,
        "matched": matched,
        "all_matches": all_matches,
        "suggestion": f"匹配成功: {matched} (补丁: {patch.vendor_name})"
    }
