"""Device Information Tool Functions / 设备信息工具函数."""

from typing import Dict, Any, List

from ..jlink_manager import jlink_manager
from ..exceptions import JLinkMCPError
from ..device_patch_manager import device_patch_manager
from ..utils import logger


def get_target_info() -> Dict[str, Any]:
    """获取目标设备（MCU）信息.

    读取连接的目标芯片的详细信息，包括设备名称、内核类型、
    Flash/RAM 大小等。

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - data: 目标设备信息（成功时）
          - device_name: 设备名称
          - core_type: 内核类型（如 Cortex-M4）
          - core_id: 内核 ID
          - device_id: 设备 ID
          - flash_size: Flash 大小（字节）
          - ram_size: RAM 大小（字节）
          - ram_addresses: RAM 地址范围
        - error: 错误信息（失败时）
    """
    try:
        info = jlink_manager.get_target_info()
        logger.info(f"获取目标信息成功: {info.device_name}")
        return {
            "success": True,
            "data": info.model_dump()
        }
    except JLinkMCPError as e:
        logger.error(f"获取目标信息失败: {e}")
        return {
            "success": False,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"获取目标信息失败: {e}")
        return {
            "success": False,
            "error": {
                "code": 1,
                "description": str(e),
                "suggestion": "请检查设备连接状态"
            }
        }


def get_target_voltage() -> Dict[str, Any]:
    """获取目标电压.

    读取目标芯片的供电电压。

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - data: 包含电压信息的数据字典
        - message: 状态信息
    """
    try:
        jlink = jlink_manager.get_jlink()
        status = jlink.hardware_status  # 属性不是方法，去掉括号
        voltage = status.VTarget / 1000.0  # 转换 mV → V
        logger.info(f"目标电压: {voltage}V")
        return {
            "success": True,
            "data": {
                "voltage_v": voltage,
                "status": "正常"
            },
            "message": f"目标电压: {voltage}V"
        }
    except JLinkMCPError as e:
        logger.error(f"获取电压失败: {e}")
        return {
            "success": False,
            "voltage": None,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"获取电压失败: {e}")
        return {
            "success": False,
            "voltage": None,
            "error": {
                "code": 1,
                "description": str(e),
                "suggestion": "请检查设备连接状态"
            }
        }


def scan_target_devices() -> Dict[str, Any]:
    """扫描目标总线上的设备.

    扫描 JTAG 链或 SWD 总线上的所有设备。

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - device_count: 发现的设备数量
        - devices: 设备 ID 列表
    """
    try:
        jlink = jlink_manager.get_jlink()

        # 获取 JTAG 链上的设备
        device_ids = []
        try:
            # 尝试获取设备 ID
            device_id = jlink.device_id()
            if device_id:
                device_ids.append(device_id)
        except Exception:
            pass

        logger.info(f"扫描到 {len(device_ids)} 个设备")
        return {
            "success": True,
            "device_count": len(device_ids),
            "devices": [{"id": did} for did in device_ids]
        }
    except JLinkMCPError as e:
        logger.error(f"扫描设备失败: {e}")
        return {
            "success": False,
            "device_count": 0,
            "devices": [],
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"扫描设备失败: {e}")
        return {
            "success": False,
            "device_count": 0,
            "devices": [],
            "error": {
                "code": 1,
                "description": str(e),
                "suggestion": "请检查设备连接状态"
            }
        }


def list_device_patches() -> Dict[str, Any]:
    """列出所有已加载的设备补丁及其支持的设备.

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - patch_count: 补丁数量
        - patches: 补丁列表，每个补丁包含:
            - vendor: 厂商名称
            - version: 补丁版本
            - device_count: 支持的设备数量
            - devices: 设备列表
            - device_names: 设备名称列表
        - message: 状态信息
    """
    try:
        patches = device_patch_manager.available_patches
        patch_info = device_patch_manager.get_patch_info()

        logger.info(f"发现 {len(patches)} 个设备补丁")
        return {
            "success": True,
            "patch_count": len(patches),
            "patches": patch_info,
            "message": f"发现 {len(patches)} 个设备补丁"
        }
    except Exception as e:
        logger.error(f"获取设备补丁列表失败: {e}")
        return {
            "success": False,
            "patch_count": 0,
            "patches": [],
            "error": {
                "code": 1,
                "description": str(e),
                "suggestion": "请检查补丁文件格式是否正确"
            }
        }
