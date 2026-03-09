"""操作相关数据模型."""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class MemoryReadRequest(BaseModel):
    """内存读取请求模型."""
    address: int = Field(..., description="起始地址（十六进制或十进制）")
    size: int = Field(..., gt=0, le=65536, description="读取大小（字节，最大 64KB）")
    width: int = Field(8, description="访问宽度（8/16/32位）")

    @field_validator('width')
    @classmethod
    def validate_width(cls, v: int) -> int:
        if v not in (8, 16, 32):
            raise ValueError("访问宽度必须是 8、16 或 32")
        return v


class MemoryWriteRequest(BaseModel):
    """内存写入请求模型."""
    address: int = Field(..., description="起始地址")
    data: bytes = Field(..., min_length=1, description="要写入的数据")
    width: int = Field(8, description="访问宽度（8/16/32位）")

    @field_validator('width')
    @classmethod
    def validate_width(cls, v: int) -> int:
        if v not in (8, 16, 32):
            raise ValueError("访问宽度必须是 8、16 或 32")
        return v


class MemoryReadResult(BaseModel):
    """内存读取结果模型."""
    address: int = Field(..., description="起始地址")
    data: bytes = Field(..., description="读取的数据")
    hex_dump: str = Field("", description="十六进制格式化字符串")


class RegisterReadResult(BaseModel):
    """寄存器读取结果模型."""
    register_name: str = Field(..., description="寄存器名称")
    value: int = Field(..., description="寄存器值")
    description: Optional[str] = Field(None, description="寄存器描述")


class FlashEraseRequest(BaseModel):
    """Flash 擦除请求模型."""
    start_address: Optional[int] = Field(None, description="起始地址（None 表示整片擦除）")
    end_address: Optional[int] = Field(None, description="结束地址（None 表示整片擦除）")
    chip_erase: bool = Field(False, description="是否整片擦除")


class FlashProgramRequest(BaseModel):
    """Flash 烧录请求模型."""
    address: int = Field(..., description="起始地址")
    data: bytes = Field(..., description="要烧录的数据")
    verify: bool = Field(True, description="烧录后是否校验")


class FlashVerifyResult(BaseModel):
    """Flash 校验结果模型."""
    matched: bool = Field(..., description="数据是否匹配")
    mismatches: list[dict] = Field(default_factory=list, description="不匹配地址列表")


class RTTConfig(BaseModel):
    """RTT 配置模型."""
    buffer_index: int = Field(0, ge=0, description="缓冲区索引")
    read_mode: str = Field("continuous", description="读取模式（continuous/once）")
    timeout_ms: int = Field(1000, ge=0, description="超时时间（毫秒）")


class DebugBreakpoint(BaseModel):
    """断点信息模型."""
    address: int = Field(..., description="断点地址")
    enabled: bool = Field(True, description="是否启用")


class CPUState(BaseModel):
    """CPU 状态模型."""
    running: bool = Field(..., description="是否正在运行")
    halted: bool = Field(..., description="是否已暂停")
    pc: Optional[int] = Field(None, description="程序计数器")
    lr: Optional[int] = Field(None, description="链接寄存器")
    sp: Optional[int] = Field(None, description="堆栈指针")
