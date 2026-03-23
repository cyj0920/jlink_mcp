"""JLink MCP - Bridge between AI and JLink Debugger / JLink MCP - AI 与 JLink 调试器的桥梁.

This is an MCP (Model Context Protocol) server that allows AI to interact with
SEGGER JLink debuggers through a standardized tool interface.
这是一个 MCP (Model Context Protocol) 服务器，允许 AI 通过标准化的工具接口
与 SEGGER JLink 调试器交互，实现芯片识别、内存操作、调试控制、固件烧录等功能。

Example / 示例:
    >>> from jlink_mcp import jlink_manager
    >>> jlink_manager.connect()
    >>> info = jlink_manager.get_target_info()
"""

__version__ = "0.1.0"
__author__ = "JLink MCP Team"

from .jlink_manager import JLinkManager, jlink_manager
from .exceptions import (
    JLinkMCPError,
    JLinkErrorCode,
    DeviceNotFoundError,
    ConnectionError,
    OperationError,
)

__all__ = [
    "JLinkManager",
    "jlink_manager",
    "JLinkMCPError",
    "JLinkErrorCode",
    "DeviceNotFoundError",
    "ConnectionError",
    "OperationError",
]
