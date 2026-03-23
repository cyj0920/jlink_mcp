"""JLink MCP Utility Functions / JLink MCP 工具函数."""

import logging
from typing import Optional


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """配置日志记录器.

    Args:
        level: 日志级别，默认为 INFO

    Returns:
        配置好的 Logger 实例
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    return logging.getLogger("jlink_mcp")


def format_bytes(data: bytes, width: int = 16) -> str:
    """格式化字节数据为十六进制字符串.

    Args:
        data: 字节数据
        width: 每行显示的字节数

    Returns:
        格式化后的字符串
    """
    lines = []
    for i in range(0, len(data), width):
        chunk = data[i:i + width]
        hex_part = " ".join(f"{b:02x}" for b in chunk)
        ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        lines.append(f"{i:08x}:  {hex_part:<{width * 3}}  {ascii_part}")
    return "\n".join(lines)


def parse_hex_string(hex_str: str) -> bytes:
    """解析十六进制字符串为字节.

    Args:
        hex_str: 十六进制字符串（如 "DEADBEEF" 或 "0xDE 0xAD"）

    Returns:
        解析后的字节数据

    Raises:
        ValueError: 如果解析失败
    """
    # 移除空格、0x 前缀等
    cleaned = hex_str.replace(" ", "").replace("0x", "").replace("0X", "")
    if len(cleaned) % 2 != 0:
        cleaned = "0" + cleaned
    try:
        return bytes.fromhex(cleaned)
    except ValueError as e:
        raise ValueError(f"无效的十六进制字符串: {hex_str}") from e


def validate_address(address: int, size: int = 4) -> None:
    """验证地址是否有效.

    Args:
        address: 内存地址
        size: 访问大小（字节）

    Raises:
        ValueError: 如果地址无效
    """
    if address < 0:
        raise ValueError(f"地址不能为负数: {address}")
    if address % size != 0:
        raise ValueError(f"地址 {address:#x} 未按 {size} 字节对齐")


def human_readable_size(size_bytes: int) -> str:
    """将字节大小转换为人类可读格式.

    Args:
        size_bytes: 字节数

    Returns:
        人类可读字符串（如 "64 KB"）
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """截断长字符串.

    Args:
        s: 原始字符串
        max_length: 最大长度
        suffix: 截断后添加的后缀

    Returns:
        截断后的字符串
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix


# 全局日志记录器
logger = setup_logging()
