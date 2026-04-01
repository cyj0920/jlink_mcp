"""JLink MCP Server - Core Service Implementation / JLink MCP 服务器 - 核心服务实现.

This is an MCP (Model Context Protocol) server that provides tool interfaces for interacting with JLink debuggers.
这是一个 MCP (Model Context Protocol) 服务器，提供与 JLink 调试器交互的工具接口。

Supported features / 支持的功能包括：
- Connection Management: Enumerate devices, connect/disconnect, status query / 连接管理：枚举设备、连接/断开、状态查询
- Device Info: Read chip information, voltage / 设备信息：读取芯片信息、电压
- Memory Operations: Read/write memory, registers / 内存操作：读写内存、寄存器
- Flash Operations: Erase, program, verify / Flash 操作：擦除、烧录、校验
- Debug Control: Reset, run/halt, step, breakpoints / 调试控制：复位、运行/暂停、单步、断点
- RTT: Real-time Transfer logging / RTT：实时传输日志
- GDB Server: Start/stop GDB debug server / GDB Server：启动/停止 GDB 调试服务器
"""

from mcp.server.fastmcp import FastMCP

from .jlink_manager import jlink_manager
from .utils import logger
from .config_manager import config_manager

# 导入所有工具函数（使用别名避免命名冲突）
from .tools.connection import (
    list_jlink_devices as _list_jlink_devices,
    connect_device as _connect_device,
    disconnect_device as _disconnect_device,
    get_connection_status as _get_connection_status,
    match_chip_name as _match_chip_name,
)
from .tools.device_info import (
    get_target_info as _get_target_info,
    get_target_voltage as _get_target_voltage,
    scan_target_devices as _scan_target_devices,
    list_device_patches as _list_device_patches,
)
from .tools.memory import (
    read_memory as _read_memory,
    write_memory as _write_memory,
    read_registers as _read_registers,
    write_register as _write_register,
)
from .tools.flash import (
    erase_flash as _erase_flash,
    program_flash as _program_flash,
    verify_flash as _verify_flash,
)
from .tools.debug import (
    reset_target as _reset_target,
    halt_cpu as _halt_cpu,
    run_cpu as _run_cpu,
    step_instruction as _step_instruction,
    get_cpu_state as _get_cpu_state,
    set_breakpoint as _set_breakpoint,
    clear_breakpoint as _clear_breakpoint,
)
from .tools.rtt import (
    rtt_start as _rtt_start,
    rtt_stop as _rtt_stop,
    rtt_read as _rtt_read,
    rtt_write as _rtt_write,
    rtt_get_status as _rtt_get_status,
)
from .gdb_server import (
    start_gdb_server as _start_gdb_server,
    stop_gdb_server as _stop_gdb_server,
    get_gdb_server_status as _get_gdb_server_status,
)
from .tools.svd import (
    list_svd_devices as _list_svd_devices,
    get_svd_peripherals as _get_svd_peripherals,
    get_svd_registers as _get_svd_registers,
    read_register_with_fields as _read_register_with_fields,
    parse_register_value as _parse_register_value,
)
from .tools.configuration import (
    get_server_config as _get_server_config,
    get_server_capabilities as _get_server_capabilities,
    diagnose_environment as _diagnose_environment,
)
from .tools.guidance import (
    get_usage_guidance as _get_usage_guidance,
    get_best_practices as _get_best_practices,
    list_scenarios as _list_scenarios,
    get_forbidden_operations as _get_forbidden_operations,
)
from .tools.semantic import (
    semantic_search_tools as _semantic_search_tools,
    get_semantic_stats as _get_semantic_stats,
)

# 创建 FastMCP 实例
mcp = FastMCP("jlink-mcp-server")


# ========================================
# Connection Management Tools (5) / 连接管理工具 (5个)
# ========================================

@mcp.tool()
async def list_jlink_devices() -> list[dict]:
    """List all connected JLink devices / 列出所有连接的 JLink 设备.

    Returns a list of all connected JLink debuggers in the system.
    返回系统中所有已连接的 JLink 调试器列表。
    Each device contains serial number, product name, and connection type.
    每个设备包含序列号、产品名称和连接类型。

    Returns:
        Device information list / 设备信息列表
    """
    return _list_jlink_devices()


@mcp.tool()
async def connect_device(serial_number: str | None = None, interface: str | None = None, chip_name: str | None = None) -> dict:
    """Connect to JLink device / 连接到 JLink 设备.

    Connects to the specified JLink debugger. If no serial number is specified, connects to the first available device.
    连接到指定的 JLink 调试器。如果不指定序列号，则连接第一个可用设备。

    Args:
        serial_number: Device serial number (optional) / 设备序列号（可选）
        interface: Target interface type (SWD/JTAG, optional, defaults to runtime config) / 目标接口类型（SWD/JTAG，可选，默认取运行时配置）
        chip_name: Target chip name (e.g., STM32F407VG, optional) / 目标芯片名称（如 STM32F407VG，可选）

    Returns:
        Connection result / 连接结果
    """
    return _connect_device(serial_number, interface, chip_name)


@mcp.tool()
async def disconnect_device() -> dict:
    """Disconnect JLink device / 断开 JLink 设备连接.

    Disconnects the current active JLink connection and releases device resources.
    断开当前活动的 JLink 连接，释放设备资源。

    Returns:
        Disconnection result / 断开结果
    """
    return _disconnect_device()


@mcp.tool()
async def get_connection_status() -> dict:
    """Get current connection status / 获取当前连接状态.

    Queries JLink connection status, target chip connection status, voltage, and other information.
    查询 JLink 连接状态、目标芯片连接状态、电压等信息。

    Returns:
        Connection status information / 连接状态信息
    """
    return _get_connection_status()


@mcp.tool()
async def match_chip_name(chip_name: str) -> dict:
    """Intelligently match chip name / 智能匹配芯片名称.

    Matches simplified chip names (e.g., FC7300F4MDD) to complete chip names
    (e.g., FC7300F4MDDxXxxxT1C). Supports prefix matching, contains matching, and fuzzy matching.
    将简化的芯片名称（如 FC7300F4MDD）匹配到完整的芯片名称
    （如 FC7300F4MDDxXxxxT1C）。支持前缀匹配、包含匹配和模糊匹配。

    Args:
        chip_name: Chip name (can be simplified or complete) / 芯片名称（可以是简化名称或完整名称）

    Returns:
        Match result, including matched (matched complete name) and all_matches (all matches) / 匹配结果，包含 matched（匹配到的完整名称）和 all_matches（所有匹配项）
    """
    return _match_chip_name(chip_name)


# ========================================
# Device Information Tools (4) / 设备信息工具 (4个)
# ========================================

@mcp.tool()
async def get_target_info() -> dict:
    """Get target device (MCU) information / 获取目标设备（MCU）信息.

    Reads detailed information about the connected target chip, including device name, core type, Flash/RAM size, etc.
    读取连接的目标芯片的详细信息，包括设备名称、内核类型、Flash/RAM 大小等。

    Returns:
        Target device information / 目标设备信息
    """
    return _get_target_info()


@mcp.tool()
async def get_target_voltage() -> dict:
    """Get target voltage / 获取目标电压.

    Reads the supply voltage of the target chip.
    读取目标芯片的供电电压。

    Returns:
        Voltage information / 电压信息
    """
    return _get_target_voltage()


@mcp.tool()
async def scan_target_devices() -> dict:
    """Scan devices on target bus / 扫描目标总线上的设备.

    Scans all devices on the JTAG chain or SWD bus.
    扫描 JTAG 链或 SWD 总线上的所有设备。

    Returns:
        Scan results / 扫描结果
    """
    return _scan_target_devices()


@mcp.tool()
async def list_device_patches() -> dict:
    """List all loaded device patches and their supported devices / 列出所有已加载的设备补丁及其支持的设备.

    Lists all available device patches (e.g., Flagchip) and their supported device lists.
    列出所有可用的设备补丁（如 Flagchip 等）及其支持的设备列表。

    Returns:
        Device patch list / 设备补丁列表
    """
    return _list_device_patches()


# ========================================
# Memory Operation Tools (4) / 内存操作工具 (4个)
# ========================================

@mcp.tool()
async def read_memory(address: int, size: int, width: int = 32) -> dict:
    """Read memory at specified address / 读取指定地址的内存.

    Args:
        address: Start address / 起始地址
        size: Read size (bytes, max 64KB) / 读取大小（字节，最大 64KB）
        width: Access width (8/16/32 bits, default 32) / 访问宽度（8/16/32位，默认 32）

    Returns:
        Memory read result / 内存读取结果
    """
    return _read_memory(address, size, width)


@mcp.tool()
async def write_memory(address: int, data: bytes, width: int = 32) -> dict:
    """Write to memory / 写入内存.

    Args:
        address: Start address / 起始地址
        data: Data to write / 要写入的数据
        width: Access width (8/16/32 bits, default 32) / 访问宽度（8/16/32位，默认 32）

    Returns:
        Write result / 写入结果
    """
    return _write_memory(address, data, width)


@mcp.tool()
async def read_registers(register_names: list[str] | None = None) -> dict:
    """Read CPU registers / 读取 CPU 寄存器.

    Args:
        register_names: Register name list (optional, None reads all general-purpose registers) / 寄存器名称列表（可选，None 则读取所有通用寄存器）

    Returns:
        Register values / 寄存器值
    """
    return _read_registers(register_names)


@mcp.tool()
async def write_register(register_name: str, value: int) -> dict:
    """Write single register / 写入单个寄存器.

    Args:
        register_name: Register name / 寄存器名称
        value: Register value / 寄存器值

    Returns:
        Write result / 写入结果
    """
    return _write_register(register_name, value)


# ========================================
# Flash Operation Tools (3) / Flash 操作工具 (3个)
# ========================================

@mcp.tool()
async def erase_flash(
    start_address: int | None = None,
    end_address: int | None = None,
    chip_erase: bool = False
) -> dict:
    """Erase Flash / 擦除 Flash.

    Args:
        start_address: Start address (optional) / 起始地址（可选）
        end_address: End address (optional) / 结束地址（可选）
        chip_erase: Whether to perform chip erase / 是否整片擦除

    Returns:
        Erase result / 擦除结果
    """
    return _erase_flash(start_address, end_address, chip_erase)


@mcp.tool()
async def program_flash(address: int, data: bytes, verify: bool = True) -> dict:
    """Program firmware to Flash / 烧录固件到 Flash.

    Args:
        address: Start address / 起始地址
        data: Data to program / 要烧录的数据
        verify: Whether to verify after programming / 烧录后是否校验

    Returns:
        Programming result / 烧录结果
    """
    return _program_flash(address, data, verify)


@mcp.tool()
async def verify_flash(address: int, data: bytes) -> dict:
    """Verify Flash content / 校验 Flash 内容.

    Args:
        address: Start address / 起始地址
        data: Expected data / 期望的数据

    Returns:
        Verification result / 校验结果
    """
    return _verify_flash(address, data)


# ========================================
# Debug Control Tools (7) / 调试控制工具 (7个)
# ========================================

@mcp.tool()
async def reset_target(reset_type: str = "normal") -> dict:
    """Reset target chip / 复位目标芯片.

    Args:
        reset_type: Reset type (normal/halt/core) / 复位类型（normal/halt/core）

    Returns:
        Reset result / 复位结果
    """
    return _reset_target(reset_type)


@mcp.tool()
async def halt_cpu() -> dict:
    """Halt CPU / 暂停 CPU.

    Returns:
        Halt result / 暂停结果
    """
    return _halt_cpu()


@mcp.tool()
async def run_cpu() -> dict:
    """Run CPU / 运行 CPU.

    Returns:
        Run result / 运行结果
    """
    return _run_cpu()


@mcp.tool()
async def step_instruction() -> dict:
    """Step one instruction / 单步执行一条指令.

    Returns:
        Step result / 单步执行结果
    """
    return _step_instruction()


@mcp.tool()
async def get_cpu_state() -> dict:
    """Get CPU state / 获取 CPU 状态.

    Returns:
        CPU state information / CPU 状态信息
    """
    return _get_cpu_state()


@mcp.tool()
async def set_breakpoint(address: int) -> dict:
    """Set breakpoint / 设置断点.

    Args:
        address: Breakpoint address / 断点地址

    Returns:
        Set result / 设置结果
    """
    return _set_breakpoint(address)


@mcp.tool()
async def clear_breakpoint(address: int) -> dict:
    """Clear breakpoint / 清除断点.

    Args:
        address: Breakpoint address / 断点地址

    Returns:
        Clear result / 清除结果
    """
    return _clear_breakpoint(address)


# ========================================
# RTT Tools (5) / RTT 工具 (5个)
# ========================================

@mcp.tool()
async def rtt_start(
    buffer_index: int = 0,
    read_mode: str = "continuous",
    timeout_ms: int = 1000
) -> dict:
    """Start RTT / 启动 RTT.

    Args:
        buffer_index: RTT buffer index / RTT 缓冲区索引
        read_mode: Read mode / 读取模式
        timeout_ms: Timeout (milliseconds) / 超时时间（毫秒）

    Returns:
        Start result / 启动结果
    """
    return _rtt_start(buffer_index, read_mode, timeout_ms)


@mcp.tool()
async def rtt_stop() -> dict:
    """Stop RTT / 停止 RTT.

    Returns:
        Stop result / 停止结果
    """
    return _rtt_stop()


@mcp.tool()
async def rtt_read(
    buffer_index: int = 0,
    size: int = 1024,
    timeout_ms: int | None = None
) -> dict:
    """Read RTT log / 读取 RTT 日志.

    Args:
        buffer_index: RTT buffer index / RTT 缓冲区索引
        size: Read size (bytes) / 读取大小（字节）
        timeout_ms: Timeout (milliseconds) / 超时时间（毫秒）

    Returns:
        Read result / 读取结果
    """
    return _rtt_read(buffer_index, size, timeout_ms)


@mcp.tool()
async def rtt_write(data: str, buffer_index: int = 0) -> dict:
    """Write data to RTT / 向 RTT 写入数据.

    Args:
        data: Data to write / 要写入的数据
        buffer_index: RTT buffer index / RTT 缓冲区索引

    Returns:
        Write result / 写入结果
    """
    return _rtt_write(data, buffer_index)


@mcp.tool()
async def rtt_get_status() -> dict:
    """Get RTT status / 获取 RTT 状态.

    Returns:
        RTT status information / RTT 状态信息
    """
    return _rtt_get_status()


# ========================================
# GDB Server Tools (3) / GDB Server 工具 (3个)
# ========================================

@mcp.tool()
async def start_gdb_server(
    host: str = "0.0.0.0",
    port: int = 2331,
    device: str | None = None,
    interface: str = "JTAG",
    speed: int = 4000
) -> dict:
    """Start GDB Server / 启动 GDB Server.

    Args:
        host: Listen address / 监听地址
        port: Listen port / 监听端口
        device: Device name / 设备名称
        interface: Interface type (SWD/JTAG, default JTAG) / 接口类型（SWD/JTAG，默认 JTAG）
        speed: Interface speed (kHz) / 接口速度（kHz）

    Returns:
        Start result / 启动结果
    """
    return _start_gdb_server(host, port, device, interface, speed)


@mcp.tool()
async def stop_gdb_server() -> dict:
    """Stop GDB Server / 停止 GDB Server.

    Returns:
        Stop result / 停止结果
    """
    return _stop_gdb_server()


@mcp.tool()
async def get_gdb_server_status() -> dict:
    """Get GDB Server status / 获取 GDB Server 状态.

    Returns:
        GDB Server status information / GDB Server 状态信息
    """
    return _get_gdb_server_status()


# ========================================
# SVD Tools (5) / SVD 工具 (5个)
# ========================================

@mcp.tool()
async def list_svd_devices() -> dict:
    """List all devices that support SVD / 列出所有支持 SVD 的设备.

    Returns a list of all devices with SVD files loaded in the system.
    返回系统中所有已加载 SVD 文件的设备列表。

    Returns:
        Device list / 设备列表
    """
    return _list_svd_devices()


@mcp.tool()
async def get_svd_peripherals(device_name: str) -> dict:
    """Get all peripherals of specified device / 获取指定设备的所有外设.

    Args:
        device_name: Device name (e.g., FC4150F1MBSxXxxxT1A) / 设备名称（如 FC4150F1MBSxXxxxT1A）

    Returns:
        Peripheral list / 外设列表
    """
    return _get_svd_peripherals(device_name)


@mcp.tool()
async def get_svd_registers(device_name: str, peripheral_name: str) -> dict:
    """Get all registers of specified peripheral / 获取指定外设的所有寄存器.

    Args:
        device_name: Device name / 设备名称
        peripheral_name: Peripheral name / 外设名称

    Returns:
        Register list / 寄存器列表
    """
    return _get_svd_registers(device_name, peripheral_name)


@mcp.tool()
async def read_register_with_fields(
    device_name: str,
    peripheral_name: str,
    register_name: str
) -> dict:
    """Read register and parse fields (combining SVD and actual read) / 读取寄存器并解析字段（结合 SVD 和实际读取）.

    Args:
        device_name: Device name / 设备名称
        peripheral_name: Peripheral name / 外设名称
        register_name: Register name / 寄存器名称

    Returns:
        Register value and field parsing result / 寄存器值和字段解析结果
    """
    return _read_register_with_fields(device_name, peripheral_name, register_name)


@mcp.tool()
async def parse_register_value(
    device_name: str,
    peripheral_name: str,
    register_name: str,
    value: int
) -> dict:
    """Parse register value (parse only, no hardware read) / 解析寄存器值（仅解析，不读取硬件）.

    Args:
        device_name: Device name / 设备名称
        peripheral_name: Peripheral name / 外设名称
        register_name: Register name / 寄存器名称
        value: Register value / 寄存器值

    Returns:
        Register value and field parsing result / 寄存器值和字段解析结果
    """
    return _parse_register_value(device_name, peripheral_name, register_name, value)


# ========================================
# Usage Guidance and Configuration Management Tools (8) / 使用指南和配置管理工具 (8个)
# ========================================

@mcp.tool()
async def get_usage_guidance(category: str | None = None, include_examples: bool = True) -> dict:
    """Get JLink MCP tool usage guidance / 获取 JLink MCP 工具使用指南.

    Provides categories, descriptions, and usage examples for all available tools.
    提供所有可用工具的分类、描述和使用示例。

    Args:
        category: Tool category (optional), supports: / 工具分类（可选），支持：
            - connection: Connection management / 连接管理
            - device_info: Device information / 设备信息
            - memory: Memory operations / 内存操作
            - flash: Flash operations / Flash 操作
            - debug: Debug control / 调试控制
            - rtt: RTT logging / RTT 日志
            - svd: SVD register parsing / SVD 寄存器解析
            None means return all categories / None 表示返回所有分类
        include_examples: Whether to include usage examples / 是否包含使用示例

    Returns:
        Usage guide, including tool categories, descriptions, and common scenarios / 使用指南，包含工具分类、描述和常见场景
    """
    return _get_usage_guidance(category, include_examples)


@mcp.tool()
async def get_best_practices(task_type: str) -> dict:
    """Get best practices for specified task type / 获取指定任务类型的最佳实践.

    Args:
        task_type: Task type, supports: / 任务类型，支持：
            - read_registers: Read registers / 读取寄存器
            - connect_device: Connect device / 连接设备
            - memory_operations: Memory operations / 内存操作
            - flash_operations: Flash operations / Flash 操作
            - debug: Debug control / 调试控制

    Returns:
        Best practices, including recommended workflows, forbidden operations, and common errors / 最佳实践，包含推荐流程、禁止操作和常见错误
    """
    return _get_best_practices(task_type)


@mcp.tool()
async def list_scenarios() -> dict:
    """List all available usage scenarios / 列出所有可用的使用场景.

    Returns:
        Scenario list, including descriptions and expected times / 场景列表，包含描述和预期时间
    """
    return _list_scenarios()


@mcp.tool()
async def get_forbidden_operations() -> dict:
    """Get list of forbidden operations / 获取禁止的操作列表.

    Returns:
        List of forbidden operations and their reasons / 禁止操作列表和原因说明
    """
    return _get_forbidden_operations()


@mcp.tool()
async def get_server_config() -> dict:
    """Get current server configuration / 获取当前服务器配置.

    Returns:
        Server configuration snapshot / 服务器配置快照
    """
    return _get_server_config()


@mcp.tool()
async def get_server_capabilities() -> dict:
    """Get current server capabilities / 获取当前服务器能力状态.

    Returns:
        Server capability summary / 服务器能力摘要
    """
    return _get_server_capabilities()


@mcp.tool()
async def diagnose_environment() -> dict:
    """Diagnose environment and resource availability / 诊断环境与资源可用性.

    Returns:
        Environment diagnosis report / 环境诊断报告
    """
    return _diagnose_environment()


# ========================================
# Semantic Search Tools (2) / 语义检索工具 (2个)
# ========================================

@mcp.tool()
async def semantic_search_tools(query: str, top_k: int = 3, threshold: float = 0.5) -> dict:
    """Semantic Search Tools - Recommend relevant tools based on natural language query / 语义搜索工具 - 根据自然语言查询推荐相关工具.

    Uses vector embedding technology to intelligently match user queries with available tools.
    使用向量嵌入技术，智能匹配用户查询与可用工具。

    This can significantly reduce AI model token consumption (expected 95-99% savings).
    可以大幅减少 AI 模型的 Token 消耗（预期节省 95-99%）。

    Examples / 示例：
        - "如何读取寄存器?" (How to read registers?) → Returns read_registers, read_register_with_fields
        - "如何烧录固件?" (How to flash firmware?) → Returns erase_flash, program_flash, verify_flash
        - "如何查看实时日志?" (How to view real-time logs?) → Returns rtt_start, rtt_read
        - "read memory" → Returns read_memory, read_registers
        - "connect to device" → Returns connect_device, list_jlink_devices

    Args:
        query: User query in natural language (Chinese or English) / 用户自然语言查询（中文或英文）
        top_k: Number of tools to return (default: 3, range: 1-10) / 返回工具数量（默认：3，范围：1-10）
        threshold: Similarity threshold (default: 0.5, range: 0-1) / 相似度阈值（默认：0.5，范围：0-1）

    Returns:
        Search results containing relevant tools with scores / 包含相关工具及分数的搜索结果

    Notes:
        - This tool requires OpenAI API key to be configured / 此工具需要配置 OpenAI API Key
        - First search will generate embeddings for all tools (may take 1-2 seconds) / 首次搜索将为所有工具生成嵌入（可能需要 1-2 秒）
        - Subsequent searches will be fast (<50ms) due to caching / 后续搜索将很快（<50ms），因为缓存
        - Supports both Chinese and English queries / 支持中文和英文查询
    """
    return _semantic_search_tools(query, top_k, threshold)


@mcp.tool()
async def get_semantic_stats() -> dict:
    """Get Semantic Search Statistics / 获取语义搜索统计信息.

    Returns statistics about the semantic search system including:
    返回语义搜索系统的统计信息，包括：
    - Total number of tools / 工具总数
    - Number of categories / 分类数量
    - Initialization status / 初始化状态
    - Embedding cache statistics / 嵌入缓存统计

    Returns:
        Statistics about the semantic search system / 语义搜索系统的统计信息
    """
    return _get_semantic_stats()


@mcp.tool()
async def get_system_prompt(prompt_name: str | None = None) -> dict:
    """Get system prompt or custom prompt / 获取系统提示词或自定义提示词.

    Args:
        prompt_name: Prompt name (optional), None returns system prompt / 提示词名称（可选），None 则返回系统提示词

    Returns:
        Prompt content / 提示词内容
    """
    try:
        if prompt_name:
            prompt = config_manager.get_custom_prompt(prompt_name)
            if prompt is None:
                available = list(config_manager.list_custom_prompts().keys())
                return {
                    "success": False,
                    "error": f"Prompt '{prompt_name}' does not exist / 提示词 '{prompt_name}' 不存在",
                    "available_prompts": available
                }
            return {
                "success": True,
                "prompt_name": prompt_name,
                "prompt": prompt
            }
        else:
            prompt = config_manager.get_system_prompt()
            return {
                "success": True,
                "prompt_name": "system",
                "prompt": prompt
            }
    except Exception as e:
        logger.error(f"Failed to get prompt: {e} / 获取提示词失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def init_server_config():
    """Initialize server configuration / 初始化服务器配置.

    Set up system prompts and custom prompts.
    设置系统提示词和自定义提示词。
    """
    # Add common custom prompts / 添加常见的自定义提示词
    config_manager.add_custom_prompt(
        "device_debug",
        """Device Debugging General Guide / 设备调试通用指南：
1. Use correct interface type (JTAG/SWD) / 使用正确的接口类型（JTAG/SWD）
2. Can use chip name abbreviations, system attempts auto-matching / 可以使用芯片名称缩写，系统尝试自动匹配
3. Must halt CPU before reading registers/memory (halt_cpu) / 读取寄存器/内存前必须暂停 CPU（halt_cpu）
4. Use match_chip_name() to verify device name when connection fails / 连接失败时使用 match_chip_name() 验证设备名称
5. Use list_device_patches() to view supported device patches / 使用 list_device_patches() 查看支持的设备补丁"""
    )

    config_manager.add_custom_prompt(
        "memory_debug",
        """Memory Debugging Guide / 内存调试指南：
1. Ensure CPU is halted before reading/writing memory (halt_cpu()) / 读写内存前确保 CPU 已暂停（halt_cpu()）
2. Verify address range is valid / 验证地址范围是否有效
3. Choose appropriate access width (8/16/32 bits) / 选择合适的访问宽度（8/16/32 位）
4. Batch read/write is more efficient than multiple single read/writes / 批量读写比多次单次读写更高效
5. Maximum read size limit is 64KB / 最大读取大小限制为 64KB"""
    )

    config_manager.add_custom_prompt(
        "flash_programming",
        """Flash Programming Guide / Flash 烧录指南：
1. Connect device using JTAG interface / 使用 JTAG 接口连接设备
2. Erase Flash first (erase_flash()) / 先擦除 Flash（erase_flash()）
3. Enable verification during programming (verify=True) / 烧录时启用校验（verify=True）
4. Flash operations are slow, please be patient / Flash 操作较慢，需要耐心等待
5. Reset device after programming completes (reset_target()) / 烧录完成后复位设备（reset_target()）"""
    )

    logger.info("Server configuration initialization completed / 服务器配置初始化完成")


def main():
    """MCP server entry function / MCP 服务器入口函数."""
    logger.info("Starting JLink MCP server (stdio mode) / 启动 JLink MCP 服务器 (std.io 模式)")

    # Initialize server configuration / 初始化服务器配置
    init_server_config()

    # Start MCP server / 启动 MCP 服务器
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
