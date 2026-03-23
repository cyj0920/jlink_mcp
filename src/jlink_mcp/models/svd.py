"""SVD (System View Description) Data Models / SVD (System View Description) 数据模型.

Defines data structures after SVD file parsing, used to describe chip peripherals,
registers, and field information.
定义 SVD 文件解析后的数据结构，用于描述芯片的外设、寄存器和字段信息。
"""

from typing import List, Optional, Dict, Tuple
from pydantic import BaseModel, Field


class EnumeratedValue(BaseModel):
    """枚举值模型.

    描述寄存器字段的枚举值，用于解释字段值的含义。
    """
    name: str = Field(..., description="枚举名称")
    value: int = Field(..., description="枚举值")
    description: Optional[str] = Field(None, description="描述")


class FieldInfo(BaseModel):
    """字段信息模型.

    描述寄存器中的单个字段（位域）。
    """
    name: str = Field(..., description="字段名称")
    description: Optional[str] = Field(None, description="字段描述")
    bit_offset: int = Field(..., ge=0, description="位偏移")
    bit_width: int = Field(..., gt=0, le=32, description="位宽")
    bit_mask: int = Field(0, description="预计算的位掩码，bit_mask = (1 << bit_width) - 1")
    access: Optional[str] = Field(None, description="访问权限")
    reset_value: Optional[int] = Field(None, description="复位值")
    enumerated_values: List[EnumeratedValue] = Field(default_factory=list, description="枚举值列表")
    # 预计算的枚举字典: {value: (name, description)}，用于 O(1) 查找
    enum_map: Dict[int, Tuple[str, Optional[str]]] = Field(default_factory=dict, description="预计算的枚举字典")


class RegisterInfo(BaseModel):
    """寄存器信息模型.

    描述外设中的单个寄存器。
    """
    name: str = Field(..., description="寄存器名称")
    description: Optional[str] = Field(None, description="寄存器描述")
    address_offset: int = Field(..., description="地址偏移")
    size: int = Field(32, description="寄存器大小（位）")
    access: Optional[str] = Field(None, description="访问权限")
    reset_value: Optional[int] = Field(None, description="复位值")
    fields: List[FieldInfo] = Field(default_factory=list, description="字段列表")


class PeripheralInfo(BaseModel):
    """外设信息模型.

    描述芯片中的单个外设（如 ADC, UART, CAN 等）。
    """
    name: str = Field(..., description="外设名称")
    description: Optional[str] = Field(None, description="外设描述")
    group_name: Optional[str] = Field(None, description="组名称")
    base_address: int = Field(..., description="基地址")
    registers: List[RegisterInfo] = Field(default_factory=list, description="寄存器列表")


class CPUInfo(BaseModel):
    """CPU 信息模型.

    描述芯片的 CPU 内核信息。
    """
    name: str = Field(..., description="CPU 名称")
    revision: Optional[str] = Field(None, description="修订版本")
    endian: Optional[str] = Field(None, description="字节序")
    mpu_present: bool = Field(False, description="是否存在 MPU")
    fpu_present: bool = Field(False, description="是否存在 FPU")
    nvic_prio_bits: Optional[int] = Field(None, description="NVIC 优先级位数")


class DeviceSVD(BaseModel):
    """设备 SVD 信息模型.

    描述整个芯片的 SVD 信息，包括 CPU 和所有外设。
    """
    name: str = Field(..., description="设备名称")
    vendor: str = Field(..., description="厂商")
    version: str = Field(..., description="版本")
    description: Optional[str] = Field(None, description="描述")
    cpu: CPUInfo = Field(..., description="CPU 信息")
    peripherals: List[PeripheralInfo] = Field(default_factory=list, description="外设列表")


class RegisterFieldResult(BaseModel):
    """寄存器字段解析结果模型.

    描述寄存器值中单个字段的解析结果。
    """
    field_name: str = Field(..., description="字段名称")
    field_value: int = Field(..., description="字段值")
    field_value_hex: str = Field(..., description="字段值的十六进制表示")
    field_description: Optional[str] = Field(None, description="字段描述")
    enum_name: Optional[str] = Field(None, description="枚举名称")
    enum_description: Optional[str] = Field(None, description="枚举描述")
    bit_range: str = Field(..., description="位范围")
    access: Optional[str] = Field(None, description="访问权限")


class RegisterReadWithFieldsResult(BaseModel):
    """带字段解析的寄存器读取结果模型.

    描述从硬件读取的寄存器值及其字段解析结果。
    """
    device_name: str = Field(..., description="设备名称")
    peripheral_name: str = Field(..., description="外设名称")
    register_name: str = Field(..., description="寄存器名称")
    register_description: Optional[str] = Field(None, description="寄存器描述")
    absolute_address: int = Field(..., description="绝对地址")
    raw_value: int = Field(..., description="原始值")
    hex_value: str = Field(..., description="十六进制值")
    binary_value: str = Field(..., description="二进制值")
    access: Optional[str] = Field(None, description="访问权限")
    reset_value: Optional[str] = Field(None, description="复位值")
    fields: List[RegisterFieldResult] = Field(default_factory=list, description="字段列表")
    field_count: int = Field(..., description="字段数量")