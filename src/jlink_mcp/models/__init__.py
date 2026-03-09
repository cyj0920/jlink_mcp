"""JLink MCP 数据模型包."""

from .base import MCPResponse, MCPError, OperationStatus
from .device import DeviceInfo, ConnectionStatus, TargetInterface
from .operations import (
    MemoryReadRequest, MemoryWriteRequest,
    FlashProgramRequest, FlashEraseRequest,
    RegisterReadResult, RTTConfig
)

__all__ = [
    "MCPResponse",
    "MCPError",
    "OperationStatus",
    "DeviceInfo",
    "ConnectionStatus",
    "TargetInterface",
    "MemoryReadRequest",
    "MemoryWriteRequest",
    "FlashProgramRequest",
    "FlashEraseRequest",
    "RegisterReadResult",
    "RTTConfig",
]
