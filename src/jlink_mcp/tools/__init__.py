"""JLink MCP Tools Package / JLink MCP 工具函数包.

This package contains all MCP tool implementations, grouped by function.
此包包含所有 MCP 工具的实现，按功能分组：

- connection: Connection management / 连接管理
- device_info: Device information / 设备信息
- memory: Memory operations / 内存操作
- flash: Flash operations / Flash 操作
- debug: Debug control / 调试控制
- rtt: RTT logging / RTT 日志
- svd: SVD register parsing / SVD 寄存器解析
- configuration: Server configuration and capability diagnostics / 服务器配置与能力诊断
- guidance: Usage guides and best practices / 使用指南和最佳实践
"""

# 导出所有工具函数，方便在 server.py 中导入
from .connection import (
    list_jlink_devices,
    connect_device,
    disconnect_device,
    get_connection_status,
)

from .device_info import (
    get_target_info,
    get_target_voltage,
    scan_target_devices,
    list_device_patches,
)

from .memory import (
    read_memory,
    write_memory,
    read_registers,
    write_register,
)

from .flash import (
    erase_flash,
    program_flash,
    verify_flash,
)

from .debug import (
    reset_target,
    halt_cpu,
    run_cpu,
    step_instruction,
    get_cpu_state,
    set_breakpoint,
    clear_breakpoint,
)

from .rtt import (
    rtt_start,
    rtt_stop,
    rtt_read,
    rtt_write,
    rtt_get_status,
)

from .svd import (
    list_svd_devices,
    get_svd_peripherals,
    get_svd_registers,
    read_register_with_fields,
    parse_register_value,
)

from .configuration import (
    get_server_config,
    get_server_capabilities,
    diagnose_environment,
)

from .guidance import (
    get_usage_guidance,
    get_best_practices,
    list_scenarios,
    get_forbidden_operations,
)

__all__ = [
    # 连接管理
    "list_jlink_devices",
    "connect_device",
    "disconnect_device",
    "get_connection_status",
    # 设备信息
    "get_target_info",
    "get_target_voltage",
    "scan_target_devices",
    "list_device_patches",
    # 内存操作
    "read_memory",
    "write_memory",
    "read_registers",
    "write_register",
    # Flash 操作
    "erase_flash",
    "program_flash",
    "verify_flash",
    # 调试控制
    "reset_target",
    "halt_cpu",
    "run_cpu",
    "step_instruction",
    "get_cpu_state",
    "set_breakpoint",
    "clear_breakpoint",
    # RTT
    "rtt_start",
    "rtt_stop",
    "rtt_read",
    "rtt_write",
    "rtt_get_status",
    # SVD
    "list_svd_devices",
    "get_svd_peripherals",
    "get_svd_registers",
    "read_register_with_fields",
    "parse_register_value",
    # 配置与诊断
    "get_server_config",
    "get_server_capabilities",
    "diagnose_environment",
    # 使用指南
    "get_usage_guidance",
    "get_best_practices",
    "list_scenarios",
    "get_forbidden_operations",
]
