"""Usage Guidance and Help Tool Functions / 使用指南和帮助工具函数.

Provides usage guides, examples, and best practices for MCP tools.
提供 MCP 工具的使用指南、示例和最佳实践。
This module does not depend on hardware connection and can be called directly.
此模块不依赖硬件连接，可直接调用。
"""

from typing import Dict, Any, List, Optional

from ..utils import logger


# 工具分类定义
TOOL_CATEGORIES = {
    "连接管理": {
        "description": "JLink 设备连接和状态管理",
        "tools": [
            "list_jlink_devices",
            "connect_device",
            "disconnect_device",
            "get_connection_status",
            "match_chip_name"
        ]
    },
    "设备信息": {
        "description": "读取目标芯片信息",
        "tools": [
            "get_target_info",
            "get_target_voltage",
            "scan_target_devices",
            "list_device_patches"
        ]
    },
    "内存操作": {
        "description": "读写内存和寄存器",
        "tools": [
            "read_memory",
            "write_memory",
            "read_registers",
            "write_register"
        ]
    },
    "Flash 操作": {
        "description": "Flash 擦除、烧录和校验",
        "tools": [
            "erase_flash",
            "program_flash",
            "verify_flash"
        ]
    },
    "调试控制": {
        "description": "CPU 控制和断点管理",
        "tools": [
            "reset_target",
            "halt_cpu",
            "run_cpu",
            "step_instruction",
            "get_cpu_state",
            "set_breakpoint",
            "clear_breakpoint"
        ]
    },
    "RTT": {
        "description": "实时传输（Real Time Transfer）日志",
        "tools": [
            "rtt_start",
            "rtt_stop",
            "rtt_read",
            "rtt_write",
            "rtt_get_status"
        ]
    },
    "SVD": {
        "description": "SVD 寄存器解析",
        "tools": [
            "list_svd_devices",
            "get_svd_peripherals",
            "get_svd_registers",
            "read_register_with_fields",
            "parse_register_value"
        ]
    },
    "GDB Server": {
        "description": "GDB 调试服务器",
        "tools": [
            "start_gdb_server",
            "stop_gdb_server",
            "get_gdb_server_status"
        ]
    },
    "使用指南": {
        "description": "使用指南、最佳实践和场景建议",
        "tools": [
            "get_usage_guidance",
            "get_best_practices",
            "list_scenarios",
            "get_forbidden_operations"
        ]
    },
    "配置诊断": {
        "description": "服务器配置、能力探测和环境诊断",
        "tools": [
            "get_server_config",
            "get_server_capabilities",
            "diagnose_environment"
        ]
    },
    "语义检索": {
        "description": "基于语义相似度的工具搜索和统计",
        "tools": [
            "semantic_search_tools",
            "get_semantic_stats"
        ]
    },
    "系统提示词": {
        "description": "获取系统提示词和自定义提示词",
        "tools": [
            "get_system_prompt"
        ]
    }
}


# 常见使用场景和工作流程
USAGE_SCENARIOS = {
    "首次连接": {
        "description": "首次连接 JLink 设备并获取基本信息",
        "steps": [
            "1. list_jlink_devices() - 列出可用设备",
            "2. connect_device(chip_name='FC7300F4MDD', interface='JTAG') - 连接设备（支持缩写）",
            "3. get_connection_status() - 确认连接状态",
            "4. get_target_info() - 获取芯片信息",
            "5. get_target_voltage() - 检查供电电压"
        ],
        "example": "connect_device(chip_name='FC7300F4MDD')  # 自动匹配到 FC7300F4MDDxXxxxT1C",
        "expected_time": "10-30 秒"
    },
    "读取寄存器": {
        "description": "读取指定寄存器的值并解析字段",
        "steps": [
            "1. connect_device(chip_name='FC7300F4MDD', interface='JTAG') - 连接设备（支持缩写）",
            "2. halt_cpu() - 暂停 CPU（必需！否则读取会失败）",
            "3. read_register_with_fields(device_name, peripheral_name, register_name) - 读取寄存器"
        ],
        "example": "read_register_with_fields('FC7300F4MDD', 'FLEXCAN0', 'ESR1')",
        "note": "读取寄存器前必须暂停 CPU（halt_cpu），这是成功读取的关键",
        "forbidden": [
            "不要调用 get_svd_peripherals() 遍历外设",
            "不要调用 get_svd_registers() 获取寄存器列表（除非未知地址）",
            "不要读取源代码文件",
            "不要跳过 halt_cpu() 步骤（读取会失败）"
        ],
        "expected_time": "2-5 秒"
    },
    "写入内存": {
        "description": "向指定内存地址写入数据",
        "steps": [
            "1. connect_device(serial_number, interface) - 连接设备",
            "2. halt_cpu() - 暂停 CPU（如果目标正在运行）",
            "3. write_memory(address, data, width) - 写入数据",
            "4. run_cpu() - 恢复运行（可选）"
        ],
        "example": "write_memory(address=0x20000000, data='00 01 02 03', width=32)",
        "expected_time": "2-5 秒"
    },
    "Flash 烧录": {
        "description": "擦除 Flash 并烧录固件",
        "steps": [
            "1. connect_device(chip_name, interface='JTAG') - 连接设备",
            "2. get_connection_status() - 确认连接",
            "3. erase_flash(start_address, end_address) - 擦除指定区域",
            "4. program_flash(address, data, verify=True) - 烧录并校验",
            "5. verify_flash(address, data) - 再次校验（可选）"
        ],
        "note": "Flash 操作较慢，需要耐心等待",
        "expected_time": "30-120 秒"
    },
    "设置断点调试": {
        "description": "设置断点并单步调试",
        "steps": [
            "1. connect_device(chip_name, interface) - 连接设备",
            "2. reset_target(reset_type='halt') - 复位并暂停",
            "3. set_breakpoint(address) - 设置断点",
            "4. run_cpu() - 运行到断点",
            "5. get_cpu_state() - 查看 CPU 状态",
            "6. read_registers() - 读取寄存器",
            "7. step_instruction() - 单步执行",
            "8. clear_breakpoint(address) - 清除断点（调试完成后）"
        ],
        "expected_time": "取决于调试复杂度"
    },
    "RTT 日志调试": {
        "description": "使用 RTT 查看实时日志",
        "steps": [
            "1. connect_device(serial_number, interface) - 连接设备",
            "2. rtt_start(buffer_index=0) - 启动 RTT",
            "3. rtt_read(size=1024) - 读取日志",
            "4. rtt_write(data) - 发送命令（可选）",
            "5. rtt_stop() - 停止 RTT（完成后）"
        ],
        "expected_time": "持续使用"
    },
    "环境诊断": {
        "description": "检查服务器配置、资源加载状态和环境依赖",
        "steps": [
            "1. get_server_config() - 查看当前运行时配置和环境变量覆盖",
            "2. get_server_capabilities() - 查看补丁、SVD、GDB Server 等能力状态",
            "3. diagnose_environment() - 检查资源路径、缺失项和建议动作"
        ],
        "example": "diagnose_environment()  # 检查 SVD/补丁/GDB Server 是否可用",
        "expected_time": "1-3 秒"
    },
    "计算波特率": {
        "description": "计算 CAN 控制器的波特率配置",
        "steps": [
            "1. connect_device(chip_name='FC7300F4MDD', interface='JTAG') - 连接设备",
            "2. halt_cpu() - 暂停 CPU（必需）",
            "3. read_register_with_fields(device, 'FLEXCAN0', 'MCR') - 检查 CAN FD 是否启用（FDEN 位）",
            "4. read_register_with_fields(device, 'FLEXCAN0', 'CTRL1') - 读取时钟源配置（CLKSRC 位）",
            "5. read_register_with_fields(device, 'FLEXCAN0', 'CTRL2') - 检查位时序扩展（BTE 位）",
            "6. 如果 BTE=1：读取 EPRS、ENCBT、EDCBT 寄存器",
            "7. 如果 BTE=0：读取 CTRL1、CBT 寄存器",
            "8. 计算：使用 PE 时钟（默认 24MHz）计算标称和数据相位波特率"
        ],
        "example": "PE=24MHz, ENPRESDIV=3, NTSEG1=7, NTSEG2=2 → 标称 500kbps, 数据 2Mbps (CAN FD)",
        "note": "默认使用 24MHz PE 时钟。如需精确计算，请通过 SCG 寄存器确认实际时钟频率",
        "expected_time": "5-10 秒"
    }
}


# 最佳实践定义
BEST_PRACTICES = {
    "read_registers": {
        "title": "读取寄存器最佳实践",
        "recommended_flow": [
            "1. connect_device(chip_name='FC7300F4MDD', interface='JTAG') - 连接设备（支持缩写）",
            "2. halt_cpu() - 暂停 CPU（必需！）",
            "3. read_register_with_fields(device_name, peripheral_name, register_name) - 直接读取寄存器"
        ],
        "forbidden": [
            "禁止使用 read_file 工具读取源代码",
            "禁止调用 get_svd_peripherals() 遍历所有外设",
            "禁止重复调用 get_svd_registers() 获取相同的寄存器列表",
            "禁止跳过 halt_cpu() 步骤（读取会失败）"
        ],
        "performance_tips": [
            "使用并行调用提高效率（如同时读取多个寄存器）",
            "缓存外设和寄存器信息，避免重复查询",
            "最小化数据传输，只读取必要的字段",
            "使用芯片名称缩写（如 FC7300F4MDD），系统自动匹配"
        ],
        "common_mistakes": [
            "❌ 跳过 halt_cpu() 步骤（读取会失败）",
            "✅ 始终在读取前暂停 CPU（halt_cpu）",
            "❌ 使用完整芯片名称（如 FC7300F4MDDxXxxxT1C）",
            "✅ 使用缩写名称（如 FC7300F4MDD）",
            "❌ 调用 get_svd_peripherals() → get_svd_registers() → read_register_with_fields()（太慢）",
            "✅ 直接调用 read_register_with_fields()（快速）",
            "❌ 连接失败后重复尝试相同的连接方式",
            "✅ 分析错误信息，使用 match_chip_name() 验证名称"
        ]
    },
    "connect_device": {
        "title": "连接设备最佳实践",
        "recommended_flow": [
            "1. list_jlink_devices() - 列出可用设备",
            "2. connect_device(chip_name='FC7300F4MDD', interface='JTAG') - 连接设备（支持缩写）",
            "3. get_connection_status() - 确认连接状态",
            "4. 连接失败时使用 match_chip_name() 验证名称"
        ],
        "recommended_practices": [
            "使用芯片名称缩写（如 FC7300F4MDD），系统会自动匹配完整名称",
            "接口默认使用 JTAG（全局默认），除非明确需要 SWD",
            "连接失败时使用 match_chip_name() 验证名称",
            "优先使用芯片名称而非序列号（更灵活）"
        ],
        "interface_selection": [
            "JTAG：全局默认推荐（通用接口）",
            "SWD：仅用于特定需求（如节省引脚、特定硬件限制）"
        ],
        "forbidden": [
            "禁止重复尝试相同的连接参数",
            "禁止在连接失败后立即再次尝试（先分析错误）",
            "禁止盲目切换接口类型（先了解目标芯片要求）"
        ],
        "troubleshooting": {
            "Unsupported device": "使用 list_device_patches() 查看支持的设备，或使用 match_chip_name() 验证名称",
            "No target connected": "检查目标芯片供电（3.3V），确保 JTAG 连接正确",
            "Unknown DEV_ID": "尝试不同的接口类型（JTAG/SWD），或检查硬件连接"
        }
    },
    "memory_operations": {
        "title": "内存操作最佳实践",
        "recommended_flow": [
            "读写内存前，确保 CPU 已暂停（halt_cpu()）",
            "验证地址范围是否有效",
            "选择合适的访问宽度（8/16/32 位）",
            "读写完成后，恢复 CPU 运行（run_cpu()）"
        ],
        "forbidden": [
            "禁止在目标运行时读取内存（可能导致错误）",
            "禁止写入只读内存区域"
        ],
        "performance_tips": [
            "批量读写比多次单次读写更高效",
            "使用 hex_dump 参数查看数据格式",
            "注意最大读取大小限制（64KB）"
        ]
    },
    "calculate_baudrate": {
        "title": "计算 CAN 波特率最佳实践",
        "recommended_flow": [
            "1. connect_device(chip_name='FC7300F4MDD', interface='JTAG') - 连接设备",
            "2. halt_cpu() - 暂停 CPU（必需）",
            "3. 读取 MCR 寄存器 - 检查 FDEN 位（CAN FD 启用状态）",
            "4. 读取 CTRL2 寄存器 - 检查 BTE 位（位时序扩展启用状态）",
            "5. 根据配置读取时序寄存器",
            "   - BTE=0: 读取 CTRL1（PRESDIV, PROPSEG, PSEG1, PSEG2）和 CBT",
            "   - BTE=1: 读取 EPRS（ENPRESDIV, EDPRESDIV）和 ENCBT、EDCBT",
            "6. 使用公式计算标称相位和数据相位波特率"
        ],
        "calculation_formula": [
            "时间量子 TQ = 1 / (PE_Clock / (PRESDIV + 1))",
            "位时间 = (1 + TSEG1 + TSEG2) × TQ",
            "波特率 = 1 / 位时间 = PE_Clock / ((PRESDIV + 1) × (1 + TSEG1 + TSEG2))"
        ],
        "default_values": {
            "PE_Clock": "24MHz（默认值，除非用户特别说明）",
            "注意": "实际波特率取决于系统时钟配置，建议查看 SCG 寄存器确认"
        },
        "forbidden": [
            "禁止在 CPU 运行时读取寄存器",
            "禁止忽略 CAN FD 配置（会影响数据相位波特率）",
            "禁止混淆标称相位和数据相位的预分频器",
            "禁止忽略 TSEG 的 +1 偏移（实际时间 = TSEG + 1）"
        ],
        "common_mistakes": [
            "❌ 使用错误预分频器（标称 vs 数据）",
            "✅ 标称相位用 ENPRESDIV，数据相位用 EDPRESDIV",
            "❌ 忽略 TSEG 的 +1 偏移",
            "✅ 时间段 = TSEG + 1（例如：NTSEG1=7 表示 8 个时间量子）",
            "❌ 假设 PE 时钟而不验证",
            "✅ 默认 24MHz，但建议从时钟树配置确认",
            "❌ 忽略 BTE 位，使用错误的寄存器",
            "✅ BTE=0 用 CTRL1/CBT，BTE=1 用 EPRS/ENCBT/EDCBT"
        ]
    }
}


def get_usage_guidance(category: str | None = None, include_examples: bool = True) -> Dict[str, Any]:
    """获取 JLink MCP 工具使用指南.

    提供所有可用工具的分类、描述和使用示例。

    Args:
        category: 工具分类（可选），支持：
            - connection: 连接管理
            - device_info: 设备信息
            - memory: 内存操作
            - flash: Flash 操作
            - debug: 调试控制
            - rtt: RTT 日志
            - svd: SVD 寄存器解析
            None 表示返回所有分类
        include_examples: 是否包含使用示例

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - total_tools: 工具总数
        - categories: 工具分类列表
        - tools: 工具详情列表（按分类）
        - scenarios: 常见使用场景
        - quick_start: 快速开始步骤
    """
    try:
        # 统计总工具数
        total_tools = sum(len(cat_info["tools"]) for cat_info in TOOL_CATEGORIES.values())

        # 筛选分类
        if category:
            category_lower = category.lower()
            filtered_categories = {
                k: v for k, v in TOOL_CATEGORIES.items()
                if k.lower() == category_lower or category_lower in k.lower()
            }
        else:
            filtered_categories = TOOL_CATEGORIES

        # 构建工具详情
        tools_detail = {}
        for cat_name, cat_info in filtered_categories.items():
            tools_detail[cat_name] = {
                "description": cat_info["description"],
                "tool_count": len(cat_info["tools"]),
                "tools": cat_info["tools"]
            }

        # 快速开始指南
        quick_start = [
            "1. 调用 get_usage_guidance() 查看可用工具",
            "2. 调用 get_server_capabilities() 或 diagnose_environment() 检查服务器能力和资源状态",
            "3. 调用 list_jlink_devices() 列出设备",
            "4. 调用 connect_device() 连接设备",
            "5. 调用 get_connection_status() 确认连接",
            "6. 根据需要调用其他工具执行操作"
        ]

        logger.info(f"获取使用指南: category={category}, tools={total_tools}")

        return {
            "success": True,
            "total_tools": total_tools,
            "categories": list(TOOL_CATEGORIES.keys()),
            "tools": tools_detail,
            "scenarios": USAGE_SCENARIOS if include_examples else {},
            "quick_start": quick_start
        }
    except Exception as e:
        logger.error(f"获取使用指南失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "请检查参数格式或联系开发者"
        }


def get_best_practices(task_type: str) -> Dict[str, Any]:
    """获取指定任务类型的最佳实践.

    Args:
        task_type: 任务类型，支持：
            - read_registers: 读取寄存器
            - connect_device: 连接设备
            - memory_operations: 内存操作
            - flash_operations: Flash 操作
            - debug: 调试控制

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - task_type: 任务类型
        - title: 最佳实践标题
        - recommended_flow: 推荐流程步骤
        - forbidden: 禁止的操作
        - performance_tips: 性能优化建议
        - common_mistakes: 常见错误和正确做法
        - troubleshooting: 故障排除指南（如果适用）
    """
    try:
        task_type_lower = task_type.lower()

        # 查找最佳实践
        practices = None
        for key, value in BEST_PRACTICES.items():
            if key.lower() == task_type_lower or task_type_lower in key.lower():
                practices = value
                break

        if not practices:
            # 提供可用的任务类型建议
            available_types = list(BEST_PRACTICES.keys())
            return {
                "success": False,
                "error": f"未找到任务类型 '{task_type}' 的最佳实践",
                "available_types": available_types,
                "suggestion": f"请使用以下任务类型之一: {', '.join(available_types)}"
            }

        logger.info(f"获取最佳实践: task_type={task_type}")

        return {
            "success": True,
            "task_type": task_type,
            **practices
        }
    except Exception as e:
        logger.error(f"获取最佳实践失败: {e}")
        return {
            "success": False,
            "error": str(e),
            "suggestion": "请检查任务类型或联系开发者"
        }


def list_scenarios() -> Dict[str, Any]:
    """列出所有可用的使用场景.

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - scenarios: 场景列表
        - total_scenarios: 场景总数
    """
    try:
        scenarios_list = []
        for name, info in USAGE_SCENARIOS.items():
            scenarios_list.append({
                "name": name,
                "description": info["description"],
                "steps_count": len(info["steps"]),
                "expected_time": info.get("expected_time", "未知")
            })

        logger.info(f"列出使用场景: {len(scenarios_list)} 个场景")

        return {
            "success": True,
            "scenarios": scenarios_list,
            "total_scenarios": len(scenarios_list)
        }
    except Exception as e:
        logger.error(f"列出使用场景失败: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def get_forbidden_operations() -> Dict[str, Any]:
    """获取禁止的操作列表.

    Returns:
        包含以下字段的字典:
        - success: 是否成功
        - forbidden: 禁止操作列表
        - reasons: 禁止原因说明
    """
    forbidden_ops = {
        "file_operations": [
            "不要使用 read_file 工具读取 src/jlink_mcp/ 下的任何源代码文件",
            "不要读取任何 .py、.md、.txt 等项目文件"
        ],
        "debugging": [
            "不要在正常业务流程中插入源码分析或调试",
            "不要读取工具函数的源代码来理解其行为",
            "不要读取配置文件或日志文件"
        ],
        "tool_usage": [
            "不要重复调用已失败的连接（尝试不同方法）",
            "不要调用 get_svd_peripherals() 遍历所有外设来查找地址",
            "不要在已知地址的情况下调用 get_svd_registers() 获取寄存器列表"
        ],
        "performance": [
            "不要在循环中重复调用相同的工具",
            "不要一次性读取大量数据（超过 64KB）",
            "不要在目标运行时读写内存"
        ]
    }

    return {
        "success": True,
        "forbidden": forbidden_ops,
        "reasons": {
            "file_operations": "源代码文件不包含运行时信息，读取会浪费时间和带宽",
            "debugging": "工具的行为通过 docstring 和返回值即可理解，无需源码分析",
            "tool_usage": "优化工具调用顺序可以提高性能和用户体验",
            "performance": "避免不必要的操作可以显著提升响应速度"
        }
    }

