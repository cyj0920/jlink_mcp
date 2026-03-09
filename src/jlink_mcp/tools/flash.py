"""Flash 操作工具函数."""

from typing import Dict, Any, Optional

from ..jlink_manager import jlink_manager
from ..exceptions import JLinkMCPError, JLinkErrorCode
from ..models.operations import FlashEraseRequest, FlashProgramRequest
from ..utils import logger, human_readable_size


def erase_flash(
    start_address: Optional[int] = None,
    end_address: Optional[int] = None,
    chip_erase: bool = False
) -> Dict[str, Any]:
    """擦除 Flash.

    Args:
        start_address: 起始地址（可选）
        end_address: 结束地址（可选）
        chip_erase: 是否整片擦除（默认 False）

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - erase_type: 擦除类型（chip/sector）
        - bytes_erased: 擦除的字节数
        - message: 状态信息
    """
    try:
        jlink = jlink_manager.get_jlink()

        if chip_erase:
            # 整片擦除
            logger.info("执行整片擦除")
            jlink.erase()
            erase_type = "chip"
            bytes_erased = 0  # 整片擦除无法知道具体字节数
        elif start_address is not None and end_address is not None:
            # 指定范围擦除
            if start_address >= end_address:
                raise JLinkMCPError(
                    JLinkErrorCode.INVALID_PARAMETER,
                    f"起始地址 {start_address:#x} 必须小于结束地址 {end_address:#x}"
                )

            size = end_address - start_address
            logger.info(f"擦除 Flash {start_address:#x} - {end_address:#x} ({human_readable_size(size)})")

            # 分扇区擦除
            jlink.erase_range(start_address, size)
            erase_type = "sector"
            bytes_erased = size
        else:
            raise JLinkMCPError(
                JLinkErrorCode.INVALID_PARAMETER,
                "必须指定 chip_erase=True 或提供 start_address 和 end_address"
            )

        logger.info("Flash 擦除成功")
        return {
            "success": True,
            "erase_type": erase_type,
            "bytes_erased": bytes_erased,
            "message": f"Flash 擦除成功（{erase_type}）"
        }
    except JLinkMCPError as e:
        logger.error(f"擦除 Flash 失败: {e}")
        return {
            "success": False,
            "erase_type": None,
            "bytes_erased": 0,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"擦除 Flash 失败: {e}")
        return {
            "success": False,
            "erase_type": None,
            "bytes_erased": 0,
            "error": {
                "code": JLinkErrorCode.ERASE_FAILED.value[0],
                "description": str(e),
                "suggestion": "请检查 Flash 是否被保护，尝试先解除保护"
            }
        }


def program_flash(address: int, data: bytes, verify: bool = True) -> Dict[str, Any]:
    """烧录固件到 Flash.

    Args:
        address: 起始地址
        data: 要烧录的数据
        verify: 烧录后是否校验（默认 True）

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - bytes_programmed: 烧录的字节数
        - verify_result: 校验结果（如果 verify=True）
        - message: 状态信息
    """
    try:
        if not data:
            raise JLinkMCPError(JLinkErrorCode.INVALID_PARAMETER, "数据不能为空")

        jlink = jlink_manager.get_jlink()

        logger.info(f"烧录 Flash {address:#x} 大小 {human_readable_size(len(data))}")
        jlink.flash_download(data, address)

        verify_result = None
        if verify:
            # 校验
            logger.info("校验 Flash")
            read_back = jlink.memory_read(address, len(data))

            if read_back == data:
                verify_result = {"matched": True, "mismatches": []}
                logger.info("Flash 校验成功")
            else:
                # 找出不匹配的位置
                mismatches = []
                for i, (a, b) in enumerate(zip(data, read_back)):
                    if a != b:
                        mismatches.append({"address": address + i, "expected": a, "actual": b})

                verify_result = {"matched": False, "mismatches": mismatches}
                logger.warning(f"Flash 校验失败，{len(mismatches)} 处不匹配")

        logger.info("Flash 烧录成功")
        return {
            "success": True,
            "bytes_programmed": len(data),
            "verify_result": verify_result,
            "message": f"成功烧录 {human_readable_size(len(data))} 到 Flash"
        }
    except JLinkMCPError as e:
        logger.error(f"烧录 Flash 失败: {e}")
        return {
            "success": False,
            "bytes_programmed": 0,
            "verify_result": None,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"烧录 Flash 失败: {e}")
        return {
            "success": False,
            "bytes_programmed": 0,
            "verify_result": None,
            "error": {
                "code": JLinkErrorCode.VERIFY_FAILED.value[0],
                "description": str(e),
                "suggestion": "请检查 Flash 是否已擦除，地址是否有效"
            }
        }


def verify_flash(address: int, data: bytes) -> Dict[str, Any]:
    """校验 Flash 内容.

    Args:
        address: 起始地址
        data: 期望的数据

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - matched: 数据是否匹配
        - mismatches: 不匹配地址列表
        - message: 状态信息
    """
    try:
        if not data:
            raise JLinkMCPError(JLinkErrorCode.INVALID_PARAMETER, "数据不能为空")

        jlink = jlink_manager.get_jlink()
        read_back = jlink.memory_read(address, len(data))

        if read_back == data:
            logger.info(f"Flash 校验成功（{len(data)} 字节）")
            return {
                "success": True,
                "matched": True,
                "mismatches": [],
                "message": f"Flash 校验成功（{len(data)} 字节）"
            }
        else:
            # 找出不匹配的位置
            mismatches = []
            for i, (a, b) in enumerate(zip(data, read_back)):
                if a != b:
                    mismatches.append({
                        "address": address + i,
                        "expected": a,
                        "actual": b
                    })

            logger.warning(f"Flash 校验失败，{len(mismatches)} 处不匹配")
            return {
                "success": True,
                "matched": False,
                "mismatches": mismatches,
                "message": f"Flash 校验失败，{len(mismatches)} 处不匹配"
            }
    except JLinkMCPError as e:
        logger.error(f"校验 Flash 失败: {e}")
        return {
            "success": False,
            "matched": False,
            "mismatches": [],
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"校验 Flash 失败: {e}")
        return {
            "success": False,
            "matched": False,
            "mismatches": [],
            "error": {
                "code": JLinkErrorCode.VERIFY_FAILED.value[0],
                "description": str(e),
                "suggestion": "请检查地址是否有效"
            }
        }