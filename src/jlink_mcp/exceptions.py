"""JLink MCP 自定义异常和错误代码定义."""

from enum import Enum
from typing import Optional


class JLinkErrorCode(Enum):
    """JLink 错误代码枚举."""

    # 通用错误 (1-99)
    UNKNOWN_ERROR = (1, "未知错误", "请检查日志或联系开发者")
    NOT_INITIALIZED = (2, "JLink 未初始化", "请先调用 connect_device 建立连接")
    ALREADY_CONNECTED = (3, "JLink 已连接", "如需重新连接，请先调用 disconnect_device")
    INVALID_PARAMETER = (4, "参数无效", "请检查传入的参数类型和值是否正确")

    # 连接错误 (100-199)
    DEVICE_NOT_FOUND = (100, "未找到 JLink 设备", "请检查设备是否已连接 USB 或供电")
    CONNECTION_FAILED = (101, "连接失败", "请检查设备连接状态，尝试重新插拔设备")
    CONNECTION_LOST = (102, "连接断开", "设备连接已断开，请重新连接")
    TARGET_NOT_CONNECTED = (103, "目标芯片未连接", "请检查目标芯片供电和连接线路")

    # 操作错误 (200-299)
    READ_FAILED = (200, "读取失败", "请检查地址是否有效，目标是否处于可访问状态")
    WRITE_FAILED = (201, "写入失败", "请检查地址、数据是否有效，Flash 是否已解锁")
    ERASE_FAILED = (202, "擦除失败", "请检查 Flash 是否被保护，尝试先解除保护")
    VERIFY_FAILED = (203, "校验失败", "数据校验不匹配，请重新烧录")
    OPERATION_TIMEOUT = (204, "操作超时", "请检查目标芯片状态，尝试复位后重试")

    # 调试错误 (300-399)
    TARGET_RUNNING = (300, "目标正在运行", "请先暂停目标 (halt_cpu) 再进行此操作")
    TARGET_HALTED = (301, "目标已暂停", "目标当前已处于暂停状态")
    RESET_FAILED = (302, "复位失败", "请检查目标芯片连接和供电状态")

    # RTT 错误 (400-499)
    RTT_NOT_STARTED = (400, "RTT 未启动", "请先调用 rtt_start 启动 RTT")
    RTT_ALREADY_STARTED = (401, "RTT 已启动", "RTT 已在运行，无需重复启动")
    RTT_BUFFER_NOT_FOUND = (402, "未找到 RTT 缓冲区", "请确保目标固件已启用 RTT 并正确配置")

    # GDB Server 错误 (500-599)
    GDB_SERVER_START_FAILED = (500, "GDB Server 启动失败", "请检查端口是否被占用，或 JLink 是否已连接")
    GDB_SERVER_NOT_RUNNING = (501, "GDB Server 未运行", "请先调用 start_gdb_server 启动服务")
    GDB_SERVER_ALREADY_RUNNING = (502, "GDB Server 已在运行", "如需重启，请先调用 stop_gdb_server")

    def __init__(self, code: int, description: str, suggestion: str):
        self.code = code
        self.description = description
        self.suggestion = suggestion

    def __str__(self) -> str:
        return f"[{self.code}] {self.description}"


class JLinkMCPError(Exception):
    """JLink MCP 基础异常类."""

    def __init__(
        self,
        error_code: JLinkErrorCode,
        detail: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        self.error_code = error_code
        self.detail = detail
        self.original_error = original_error
        super().__init__(self.message)

    @property
    def message(self) -> str:
        """生成完整的错误信息."""
        parts = [str(self.error_code)]
        if self.detail:
            parts.append(f"详情: {self.detail}")
        if self.original_error:
            parts.append(f"原始错误: {str(self.original_error)}")
        parts.append(f"建议: {self.error_code.suggestion}")
        return "\n".join(parts)

    def to_dict(self) -> dict:
        """转换为字典格式."""
        return {
            "code": self.error_code.code,
            "description": self.error_code.description,
            "detail": self.detail,
            "suggestion": self.error_code.suggestion,
            "original_error": str(self.original_error) if self.original_error else None
        }


class DeviceNotFoundError(JLinkMCPError):
    """设备未找到异常."""

    def __init__(self, detail: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(JLinkErrorCode.DEVICE_NOT_FOUND, detail, original_error)


class ConnectionError(JLinkMCPError):
    """连接错误异常."""

    def __init__(self, detail: Optional[str] = None, original_error: Optional[Exception] = None):
        super().__init__(JLinkErrorCode.CONNECTION_FAILED, detail, original_error)


class OperationError(JLinkMCPError):
    """操作错误异常."""

    def __init__(
        self,
        error_code: JLinkErrorCode = JLinkErrorCode.UNKNOWN_ERROR,
        detail: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(error_code, detail, original_error)


class RTTError(JLinkMCPError):
    """RTT 相关异常."""

    def __init__(
        self,
        error_code: JLinkErrorCode = JLinkErrorCode.RTT_NOT_STARTED,
        detail: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(error_code, detail, original_error)


class GDBServerError(JLinkMCPError):
    """GDB Server 相关异常."""

    def __init__(
        self,
        error_code: JLinkErrorCode = JLinkErrorCode.GDB_SERVER_START_FAILED,
        detail: Optional[str] = None,
        original_error: Optional[Exception] = None
    ):
        super().__init__(error_code, detail, original_error)
