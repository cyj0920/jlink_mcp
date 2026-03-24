"""RTT (Real Time Transfer) Tool Functions / RTT (Real Time Transfer) 工具函数."""

from typing import Dict, Any, Optional

from ..jlink_manager import jlink_manager
from ..exceptions import JLinkMCPError, JLinkErrorCode, RTTError
from ..utils import logger


# 全局 RTT 状态
_rtt_started = False
_rtt_config = {
    "buffer_index": 0,
    "read_mode": "continuous",
    "timeout_ms": 1000
}


def rtt_start(
    buffer_index: int = 0,
    read_mode: str = "continuous",
    timeout_ms: int = 1000
) -> Dict[str, Any]:
    """启动 RTT.

    Args:
        buffer_index: RTT 缓冲区索引（默认 0）
        read_mode: 读取模式（continuous/once，默认 continuous）
        timeout_ms: 超时时间（毫秒，默认 1000）

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - buffer_index: 缓冲区索引
        - message: 状态信息
    """
    global _rtt_started, _rtt_config

    try:
        if _rtt_started:
            raise RTTError(
                JLinkErrorCode.RTT_ALREADY_STARTED,
                "RTT 已在运行",
                "如需重新启动，请先调用 rtt_stop"
            )

        jlink = jlink_manager.get_jlink()

        # 配置 RTT
        logger.info(f"启动 RTT，缓冲区索引: {buffer_index}")
        jlink.rtt_start(buffer_index)

        _rtt_started = True
        _rtt_config = {
            "buffer_index": buffer_index,
            "read_mode": read_mode,
            "timeout_ms": timeout_ms
        }

        return {
            "success": True,
            "buffer_index": buffer_index,
            "message": f"RTT 已启动（缓冲区 {buffer_index}）"
        }
    except RTTError as e:
        logger.error(f"启动 RTT 失败: {e}")
        return {
            "success": False,
            "buffer_index": buffer_index,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"启动 RTT 失败: {e}")
        return {
            "success": False,
            "buffer_index": buffer_index,
            "error": {
                "code": JLinkErrorCode.RTT_NOT_STARTED.value[0],
                "description": str(e),
                "suggestion": "请确保目标固件已启用 RTT 并正确配置"
            }
        }


def rtt_stop() -> Dict[str, Any]:
    """停止 RTT.

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - message: 状态信息
    """
    global _rtt_started

    try:
        if not _rtt_started:
            raise RTTError(
                JLinkErrorCode.RTT_NOT_STARTED,
                "RTT 未启动",
                "无需停止"
            )

        jlink = jlink_manager.get_jlink()
        jlink.rtt_stop()

        _rtt_started = False
        logger.info("RTT 已停止")

        return {
            "success": True,
            "message": "RTT 已停止"
        }
    except RTTError as e:
        logger.error(f"停止 RTT 失败: {e}")
        return {
            "success": False,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"停止 RTT 失败: {e}")
        return {
            "success": False,
            "error": {
                "code": JLinkErrorCode.UNKNOWN_ERROR.value[0],
                "description": str(e),
                "suggestion": "请检查 RTT 状态"
            }
        }


def rtt_read(
    buffer_index: int = 0,
    size: int = 1024,
    timeout_ms: Optional[int] = None
) -> Dict[str, Any]:
    """读取 RTT 日志.

    Args:
        buffer_index: RTT 缓冲区索引（默认 0）
        size: 读取大小（字节，默认 1024）
        timeout_ms: 超时时间（毫秒，None 则使用配置的值）

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - data: 读取的数据（字符串）
        - bytes_read: 读取的字节数
        - message: 状态信息
    """
    global _rtt_started, _rtt_config

    try:
        if not _rtt_started:
            raise RTTError(
                JLinkErrorCode.RTT_NOT_STARTED,
                "RTT 未启动",
                "请先调用 rtt_start 启动 RTT"
            )

        jlink = jlink_manager.get_jlink()

        # 使用配置的超时时间
        if timeout_ms is None:
            timeout_ms = _rtt_config.get("timeout_ms", 1000)

        # 读取 RTT 数据
        data = jlink.rtt_read(buffer_index, size, timeout_ms)

        if data:
            # 尝试解码为字符串
            try:
                text_data = data.decode('utf-8', errors='ignore')
            except Exception:
                text_data = data.decode('latin1')

            logger.info(f"RTT 读取 {len(data)} 字节")
            return {
                "success": True,
                "data": text_data,
                "bytes_read": len(data),
                "message": f"成功读取 {len(data)} 字节"
            }
        else:
            return {
                "success": True,
                "data": "",
                "bytes_read": 0,
                "message": "RTT 缓冲区为空"
            }

    except RTTError as e:
        logger.error(f"读取 RTT 失败: {e}")
        return {
            "success": False,
            "data": "",
            "bytes_read": 0,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"读取 RTT 失败: {e}")
        return {
            "success": False,
            "data": "",
            "bytes_read": 0,
            "error": {
                "code": JLinkErrorCode.RTT_NOT_STARTED.value[0],
                "description": str(e),
                "suggestion": "请检查 RTT 是否已启动，缓冲区索引是否正确"
            }
        }


def rtt_write(data: str, buffer_index: int = 0) -> Dict[str, Any]:
    """向 RTT 写入数据.

    Args:
        data: 要写入的数据（字符串）
        buffer_index: RTT 缓冲区索引（默认 0）

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - bytes_written: 写入的字节数
        - message: 状态信息
    """
    global _rtt_started

    try:
        if not _rtt_started:
            raise RTTError(
                JLinkErrorCode.RTT_NOT_STARTED,
                "RTT 未启动",
                "请先调用 rtt_start 启动 RTT"
            )

        jlink = jlink_manager.get_jlink()

        # 编码数据
        data_bytes = data.encode('utf-8')

        # 写入 RTT
        bytes_written = jlink.rtt_write(buffer_index, data_bytes)

        logger.info(f"RTT 写入 {bytes_written} 字节")
        return {
            "success": True,
            "bytes_written": bytes_written,
            "message": f"成功写入 {bytes_written} 字节"
        }
    except RTTError as e:
        logger.error(f"RTT 写入失败: {e}")
        return {
            "success": False,
            "bytes_written": 0,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"RTT 写入失败: {e}")
        return {
            "success": False,
            "bytes_written": 0,
            "error": {
                "code": JLinkErrorCode.RTT_NOT_STARTED.value[0],
                "description": str(e),
                "suggestion": "请检查 RTT 是否已启动"
            }
        }


def rtt_get_status() -> Dict[str, Any]:
    """获取 RTT 状态.

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - started: 是否已启动
        - buffer_index: 当前缓冲区索引
        - config: 当前配置
    """
    global _rtt_started, _rtt_config

    return {
        "success": True,
        "started": _rtt_started,
        "buffer_index": _rtt_config.get("buffer_index", 0) if _rtt_started else None,
        "config": _rtt_config if _rtt_started else None,
        "message": "RTT 已启动" if _rtt_started else "RTT 未启动"
    }