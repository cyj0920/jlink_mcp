"""Connection Management Tool Functions / 连接管理工具函数."""

from typing import List, Dict, Any

from ..jlink_manager import jlink_manager
from ..models.device import DeviceInfo, ConnectionStatus, TargetInterface
from ..utils import logger
from ..config_manager import config_manager


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
    return [device.model_dump() for device in devices]


def connect_device(serial_number: str | None = None, interface: str | None = None, chip_name: str | None = None) -> Dict[str, Any]:
    """连接到 JLink 设备.

    连接到指定的 JLink 调试器。如果不指定序列号，则连接第一个可用设备。
    连接成功后，可以执行其他操作如读写内存、控制调试等。

    Args:
        serial_number: 设备序列号（可选，None 则连接第一个设备）
        interface: 目标接口类型，支持 "SWD" 或 "JTAG"（可选，默认从配置读取，默认值为 JTAG）
        chip_name: 目标芯片名称（可选，支持缩写自动匹配，如 FC7300F4MDD）

    Returns:
        连接结果，包含:
        - success: 是否成功
        - serial_number: 连接的设备序列号
        - message: 状态信息
    """
    try:
        # 从配置读取默认接口（如果未指定）
        if interface is None:
            config = config_manager.get_config()
            interface = config.default_interface  # 默认 JTAG
            logger.debug(f"使用配置的默认接口: {interface}")

        interface_enum = TargetInterface(interface.upper())
        jlink_manager.connect(serial_number, interface_enum, chip_name)
        status = jlink_manager.get_connection_status()

        logger.info(f"成功连接到设备: {status.device_serial}")
        return {
            "success": True,
            "serial_number": status.device_serial,
            "message": f"成功连接到设备 {status.device_serial}，接口: {interface}"
        }
    except Exception as e:
        logger.error(f"连接失败: {e}")
        error_msg = str(e)

        # 检查是否是设备不支持的错误
        if "unsupported device" in error_msg.lower() or "not found" in error_msg.lower():
            from ..device_patch_manager import device_patch_manager
            if chip_name:
                # 提供设备名称建议
                suggestions = device_patch_manager.get_device_name_suggestions(chip_name)
                error_msg = f"设备 '{chip_name}' 不受支持。\n{suggestions}"

        return {
            "success": False,
            "serial_number": None,
            "message": error_msg
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
        return {
            "success": False,
            "message": str(e)
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
        - message: 状态信息
    """
    try:
        status = jlink_manager.get_connection_status()
        return {
            "success": True,
            "data": status.model_dump(),
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

    # 获取最佳匹配（使用设备补丁管理器）
    match_result = device_patch_manager.match_device_name(chip_name)

    if not match_result:
        # 获取所有相似的设备
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

    # 获取所有相似的设备
    all_matches = device_patch_manager.find_similar_devices(chip_name, limit=10)

    logger.info(f"芯片名称匹配成功: '{chip_name}' -> '{matched}' (补丁: {patch.vendor_name})")
    return {
        "success": True,
        "input": chip_name,
        "matched": matched,
        "all_matches": all_matches,
        "suggestion": f"匹配成功: {matched} (补丁: {patch.vendor_name})"
    }
