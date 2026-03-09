"""JLink MCP 基础数据模型."""

from typing import Generic, Optional, TypeVar, Any
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum


class OperationStatus(str, Enum):
    """操作状态枚举."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"


class MCPError(BaseModel):
    """MCP 错误信息模型."""
    code: int = Field(..., description="错误代码")
    description: str = Field(..., description="错误描述")
    detail: Optional[str] = Field(None, description="详细错误信息")
    suggestion: str = Field(..., description="修复建议")


T = TypeVar('T')


class MCPResponse(BaseModel, Generic[T]):
    """MCP 统一响应模型.

    所有 MCP 工具函数都应返回此格式的响应，确保一致的错误处理和类型安全。
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    status: OperationStatus = Field(..., description="操作状态")
    data: Optional[T] = Field(None, description="响应数据")
    message: str = Field("", description="附加消息")
    error: Optional[MCPError] = Field(None, description="错误信息（仅在出错时）")

    @classmethod
    def success(cls, data: T, message: str = "") -> "MCPResponse[T]":
        """创建成功响应."""
        return cls(
            status=OperationStatus.SUCCESS,
            data=data,
            message=message
        )

    @classmethod
    def create_error(
        cls,
        error_code: int,
        description: str,
        suggestion: str,
        detail: Optional[str] = None
    ) -> "MCPResponse[Any]":
        """创建错误响应."""
        return cls(
            status=OperationStatus.ERROR,
            message=description,
            error=MCPError(
                code=error_code,
                description=description,
                detail=detail,
                suggestion=suggestion
            )
        )

    @classmethod
    def warning(cls, data: T, message: str) -> "MCPResponse[T]":
        """创建警告响应."""
        return cls(
            status=OperationStatus.WARNING,
            data=data,
            message=message
        )


class ProgressInfo(BaseModel):
    """进度信息模型."""
    current: int = Field(..., description="当前进度")
    total: int = Field(..., description="总进度")
    percentage: float = Field(..., description="完成百分比")
    message: str = Field("", description="进度描述")

    @property
    def is_complete(self) -> bool:
        """是否已完成."""
        return self.current >= self.total


class PaginatedResult(BaseModel, Generic[T]):
    """分页结果模型."""
    items: list[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总数量")
    page: int = Field(1, description="当前页")
    page_size: int = Field(10, description="每页大小")

    @property
    def total_pages(self) -> int:
        """总页数."""
        return (self.total + self.page_size - 1) // self.page_size

    @property
    def has_next(self) -> bool:
        """是否有下一页."""
        return self.page < self.total_pages

    @property
    def has_prev(self) -> bool:
        """是否有上一页."""
        return self.page > 1
