"""内存操作工具函数."""

from typing import Dict, Any, List, Optional

from ..jlink_manager import jlink_manager
from ..exceptions import JLinkMCPError, JLinkErrorCode
from ..models.operations import MemoryReadRequest, MemoryWriteRequest, RegisterReadResult
from ..utils import logger, validate_address, format_bytes


def read_memory(address: int, size: int, width: int = 32) -> Dict[str, Any]:
    """读取指定地址的内存.

    Args:
        address: 起始地址（十进制或十六进制字符串）
        size: 读取大小（字节，最大 64KB）
        width: 访问宽度（8/16/32位，默认 32）

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - data: 读取的数据（字节列表）
        - hex_dump: 十六进制格式化字符串
        - address: 起始地址
    """
    try:
        # 参数验证
        if size <= 0:
            raise JLinkMCPError(JLinkErrorCode.INVALID_PARAMETER, f"大小必须大于 0: {size}")
        if size > 65536:
            raise JLinkMCPError(JLinkErrorCode.INVALID_PARAMETER, f"大小超过最大限制 64KB: {size}")
        if width not in (8, 16, 32):
            raise JLinkMCPError(JLinkErrorCode.INVALID_PARAMETER, f"宽度必须是 8/16/32: {width}")

        validate_address(address, width // 8)

        jlink = jlink_manager.get_jlink()
        
        # 添加：检查目标是否暂停（解决 -3 错误的主要原因）
        try:
            if hasattr(jlink, 'halted') and not jlink.halted():
                logger.warning(f"目标正在运行，尝试暂停后读取内存 {address:#x}")
                jlink.halt()
        except Exception:
            # 如果无法检查或暂停状态，继续尝试读取
            pass
        
        data = jlink.memory_read(address, size)

        hex_dump = format_bytes(data)
        logger.info(f"读取内存 {address:#x} 大小 {size} 字节成功")

        return {
            "success": True,
            "data": list(data),
            "hex_dump": hex_dump,
            "address": address
        }
    except JLinkMCPError as e:
        logger.error(f"读取内存失败: {e}")
        return {
            "success": False,
            "data": [],
            "hex_dump": "",
            "error": e.to_dict()
        }
    except Exception as e:
        error_msg = str(e)
        error_code = JLinkErrorCode.READ_FAILED
        suggestion = "请检查地址是否有效，目标是否处于可访问状态"
        
        # 解析 pylink-square 错误信息，提供更具体的错误码
        error_msg_lower = error_msg.lower()
        if "-3" in error_msg or "running" in error_msg_lower or "busy" in error_msg_lower:
            error_code = JLinkErrorCode.TARGET_RUNNING
            suggestion = "目标正在运行，请先调用 halt_cpu 暂停目标后再读取内存"
        elif "not connected" in error_msg_lower or "no device" in error_msg_lower:
            error_code = JLinkErrorCode.TARGET_NOT_CONNECTED
            suggestion = "目标芯片未连接，请检查硬件连接"
        elif "invalid address" in error_msg_lower or "alignment" in error_msg_lower:
            error_code = JLinkErrorCode.INVALID_PARAMETER
            suggestion = "地址无效或未对齐，请检查地址和访问宽度"
        
        logger.error(f"读取内存失败: {error_msg}")
        return {
            "success": False,
            "data": [],
            "hex_dump": "",
            "error": {
                "code": error_code.value[0],
                "description": error_msg,
                "suggestion": suggestion
            }
        }


def write_memory(address: int, data: bytes, width: int = 32) -> Dict[str, Any]:
    """写入内存.

    Args:
        address: 起始地址
        data: 要写入的数据（字节列表）
        width: 访问宽度（8/16/32位，默认 32）

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - bytes_written: 写入的字节数
        - message: 状态信息
    """
    try:
        if not data:
            raise JLinkMCPError(JLinkErrorCode.INVALID_PARAMETER, "数据不能为空")

        validate_address(address, width // 8)

        jlink = jlink_manager.get_jlink()
        jlink.memory_write(address, data)

        logger.info(f"写入内存 {address:#x} 大小 {len(data)} 字节成功")

        return {
            "success": True,
            "bytes_written": len(data),
            "message": f"成功写入 {len(data)} 字节到地址 {address:#x}"
        }
    except JLinkMCPError as e:
        logger.error(f"写入内存失败: {e}")
        return {
            "success": False,
            "bytes_written": 0,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"写入内存失败: {e}")
        return {
            "success": False,
            "bytes_written": 0,
            "error": {
                "code": JLinkErrorCode.WRITE_FAILED.value[0],
                "description": str(e),
                "suggestion": "请检查地址、数据是否有效，Flash 是否已解锁"
            }
        }


def read_registers(register_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """读取 CPU 寄存器.

    Args:
        register_names: 寄存器名称列表，None 则读取所有通用寄存器

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - registers: 寄存器值列表 [{name, value}, ...]
    """
    try:
        jlink = jlink_manager.get_jlink()

        if register_names:
            # 读取指定寄存器
            registers = []
            for name in register_names:
                try:
                    value = jlink.register_read(name)
                    registers.append({"name": name, "value": value})
                except Exception as e:
                    logger.warning(f"读取寄存器 {name} 失败: {e}")
        else:
            # 读取所有通用寄存器（ARM Cortex-M）
            register_list = [
                "R0", "R1", "R2", "R3", "R4", "R5", "R6", "R7",
                "R8", "R9", "R10", "R11", "R12",
                "R13 (SP)", "R14 (LR)", "R15 (PC)",
                "XPSR", "MSP", "PSP"
            ]
            registers = []
            for name in register_list:
                try:
                    value = jlink.register_read(name)
                    registers.append({"name": name, "value": value})
                except Exception as e:
                    logger.debug(f"寄存器 {name} 不可用: {e}")

        logger.info(f"读取 {len(registers)} 个寄存器成功")
        return {
            "success": True,
            "registers": registers
        }
    except JLinkMCPError as e:
        logger.error(f"读取寄存器失败: {e}")
        return {
            "success": False,
            "registers": [],
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"读取寄存器失败: {e}")
        return {
            "success": False,
            "registers": [],
            "error": {
                "code": JLinkErrorCode.READ_FAILED.value[0],
                "description": str(e),
                "suggestion": "请检查目标是否已暂停，寄存器名称是否正确"
            }
        }


def write_register(register_name: str, value: int) -> Dict[str, Any]:
    """写入单个寄存器.

    Args:
        register_name: 寄存器名称（如 R0, PC, SP 等）
        value: 寄存器值

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - register_name: 寄存器名称
        - value: 写入的值
    """
    try:
        if not register_name:
            raise JLinkMCPError(JLinkErrorCode.INVALID_PARAMETER, "寄存器名称不能为空")

        jlink = jlink_manager.get_jlink()
        jlink.register_write(register_name, value)

        logger.info(f"写入寄存器 {register_name} = {value:#x} 成功")

        return {
            "success": True,
            "register_name": register_name,
            "value": value,
            "message": f"成功写入寄存器 {register_name} = {value:#x}"
        }
    except JLinkMCPError as e:
        logger.error(f"写入寄存器失败: {e}")
        return {
            "success": False,
            "register_name": register_name,
            "value": value,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"写入寄存器失败: {e}")
        return {
            "success": False,
            "register_name": register_name,
            "value": value,
            "error": {
                "code": JLinkErrorCode.WRITE_FAILED.value[0],
                "description": str(e),
                "suggestion": "请检查寄存器名称是否正确，目标是否已暂停"
            }
        }