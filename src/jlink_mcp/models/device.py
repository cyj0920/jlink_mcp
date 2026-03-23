"""Device Related Data Models / 设备相关数据模型."""

from typing import Optional
from pydantic import BaseModel, Field
from enum import Enum


class TargetInterface(str, Enum):
    """目标接口类型."""
    JTAG = "JTAG"
    SWD = "SWD"
    FINE = "FINE"
    ICSP = "ICSP"
    SPI = "SPI"
    C2 = "C2"


class ConnectionStatus(BaseModel):
    """连接状态模型."""
    connected: bool = Field(..., description="是否已连接")
    device_serial: Optional[str | int] = Field(None, description="设备序列号")
    target_interface: Optional[TargetInterface] = Field(None, description="目标接口类型")
    target_voltage: Optional[float] = Field(None, description="目标电压（V）")
    target_connected: bool = Field(False, description="目标芯片是否已连接")
    firmware_version: Optional[str] = Field(None, description="JLink 固件版本")


class DeviceInfo(BaseModel):
    """JLink 设备信息模型."""
    serial_number: str = Field(..., description="设备序列号")
    product_name: str = Field(..., description="产品名称")
    firmware_version: str = Field(..., description="固件版本")
    hardware_version: Optional[str] = Field(None, description="硬件版本")
    connection_type: str = Field(..., description="连接类型（USB/ETH）")


class TargetDeviceInfo(BaseModel):
    """目标设备（MCU）信息模型."""
    device_name: Optional[str] = Field(None, description="设备名称")
    core_type: Optional[str] = Field(None, description="内核类型")
    core_id: Optional[int] = Field(None, description="内核 ID")
    device_id: Optional[int] = Field(None, description="设备 ID")
    flash_size: Optional[int] = Field(None, description="Flash 大小（字节）")
    ram_size: Optional[int] = Field(None, description="RAM 大小（字节）")
    ram_addresses: list[tuple[int, int]] = Field(
        default_factory=list,
        description="RAM 地址范围列表 [(start, size), ...]"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "device_name": "STM32F407VG",
                "core_type": "Cortex-M4",
                "core_id": 0x410FC241,
                "device_id": 0x413,
                "flash_size": 1048576,
                "ram_size": 131072,
                "ram_addresses": [[0x20000000, 131072]]
            }
        }


class GDBServerStatus(BaseModel):
    """GDB Server 状态模型."""
    running: bool = Field(..., description="是否正在运行")
    host: Optional[str] = Field(None, description="监听地址")
    port: Optional[int] = Field(None, description="监听端口")
    device_name: Optional[str] = Field(None, description="设备名称")
    interface: Optional[TargetInterface] = Field(None, description="接口类型")
