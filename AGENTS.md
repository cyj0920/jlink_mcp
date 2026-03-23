# JLink MCP - AI Agent 开发指南

## 项目概述 / Project Overview

JLink MCP 是一个基于 Model Context Protocol (MCP) 的 J-Link 调试器服务器，允许 AI 助手通过标准化接口与 J-Link 硬件调试器交互。

**核心功能：**
- 设备连接管理（SWD/JTAG）
- 内存读写操作
- Flash 编程（擦除/烧录/校验）
- 调试控制（暂停/运行/单步/断点）
- SVD 寄存器解析
- RTT 实时数据传输
- GDB Server 支持

## 项目结构 / Project Structure

```
jlink_mcp/
├── src/jlink_mcp/           # 源代码
│   ├── server.py            # MCP 服务器主入口
│   ├── jlink_manager.py     # JLink 设备管理器（单例）
│   ├── svd_manager.py       # SVD 文件管理器（单例）
│   ├── config_manager.py    # 配置管理器（单例）
│   ├── device_patch_manager.py  # 设备补丁管理器
│   ├── gdb_server.py        # GDB Server 管理
│   ├── exceptions.py        # 自定义异常和错误码
│   ├── utils.py             # 工具函数
│   ├── models/              # Pydantic 数据模型
│   │   ├── base.py          # 基础响应模型
│   │   ├── device.py        # 设备相关模型
│   │   ├── operations.py    # 操作相关模型
│   │   └── svd.py           # SVD 解析模型
│   ├── plugins/             # 设备补丁插件
│   │   └── flagchip_patch.py # Flagchip 设备补丁
│   └── tools/               # MCP 工具函数
│       ├── connection.py    # 连接管理
│       ├── device_info.py   # 设备信息
│       ├── memory.py        # 内存操作
│       ├── flash.py         # Flash 操作
│       ├── debug.py         # 调试控制
│       ├── rtt.py           # RTT 日志
│       ├── svd.py           # SVD 寄存器
│       └── guidance.py      # 使用指南
├── tests/                   # 测试目录
│   ├── unit/                # 单元测试
│   ├── mock/                # Mock 测试
│   └── performance/         # 性能测试
├── docs/                    # 文档
├── pyproject.toml           # 项目配置
└── pytest.ini               # 测试配置
```

## 技术栈 / Tech Stack

- **Python**: 3.10+
- **MCP SDK**: mcp>=1.26.0
- **JLink 库**: pylink-square>=2.0.0
- **数据验证**: Pydantic>=2.12.0
- **测试**: pytest>=8.0.0, pytest-asyncio, pytest-benchmark

## 开发命令 / Development Commands

### 安装

```bash
# 开发模式安装
pip install -e .

# 使用 UV 安装（推荐）
pip install uv
uv pip install -e .

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行

```bash
# 启动 MCP 服务器
python -m jlink_mcp

# 或直接运行
jlink-mcp
```

### 测试

```bash
# 运行所有测试
pytest

# 运行单元测试（不需要硬件）
pytest -m unit

# 运行集成测试（需要硬件）
pytest -m integration

# 运行特定测试
pytest tests/unit/test_models.py -v

# 生成覆盖率报告
pytest --cov=src/jlink_mcp --cov-report=html

# 运行性能基准测试
pytest -m benchmark
```

### 代码质量

```bash
# 格式化代码
black src/

# Lint 检查
ruff check src/

# 类型检查
mypy src/
```

## 架构设计 / Architecture

### 单例模式

项目使用单例模式管理核心组件：

- `JLinkManager`: 管理 JLink 连接
- `SVDManager`: 管理 SVD 文件解析
- `ConfigManager`: 管理配置
- `DevicePatchManager`: 管理设备补丁

### 插件架构

设备补丁系统支持插件化扩展：

```python
# 创建自定义补丁
from jlink_mcp.device_patch_interface import DevicePatchInterface

class MyDevicePatch(DevicePatchInterface):
    @property
    def vendor_name(self) -> str:
        return "MyVendor"
    
    def match_device_name(self, chip_name: str) -> Optional[str]:
        # 实现设备名称匹配逻辑
        pass
```

### 工具函数组织

每个 MCP 工具函数都遵循统一的返回格式：

```python
{
    "success": bool,          # 操作是否成功
    "data": Any,              # 返回数据
    "message": str,           # 状态信息
    "error": Optional[dict]   # 错误详情
}
```

## MCP 工具列表 / MCP Tools

### 连接管理 (5个)
| 工具 | 功能 |
|------|------|
| `list_jlink_devices` | 列出连接的 JLink 设备 |
| `connect_device` | 连接到设备 |
| `disconnect_device` | 断开连接 |
| `get_connection_status` | 获取连接状态 |
| `match_chip_name` | 智能匹配芯片名称 |

### 设备信息 (4个)
| 工具 | 功能 |
|------|------|
| `get_target_info` | 获取目标设备信息 |
| `get_target_voltage` | 获取目标电压 |
| `scan_target_devices` | 扫描总线设备 |
| `list_device_patches` | 列出设备补丁 |

### 内存操作 (4个)
| 工具 | 功能 |
|------|------|
| `read_memory` | 读取内存 |
| `write_memory` | 写入内存 |
| `read_registers` | 读取 CPU 寄存器 |
| `write_register` | 写入寄存器 |

### Flash 操作 (3个)
| 工具 | 功能 |
|------|------|
| `erase_flash` | 擦除 Flash |
| `program_flash` | 烧录 Flash |
| `verify_flash` | 校验 Flash |

### 调试控制 (7个)
| 工具 | 功能 |
|------|------|
| `reset_target` | 复位目标 |
| `halt_cpu` | 暂停 CPU |
| `run_cpu` | 运行 CPU |
| `step_instruction` | 单步执行 |
| `get_cpu_state` | 获取 CPU 状态 |
| `set_breakpoint` | 设置断点 |
| `clear_breakpoint` | 清除断点 |

### RTT (5个)
| 工具 | 功能 |
|------|------|
| `rtt_start` | 启动 RTT |
| `rtt_stop` | 停止 RTT |
| `rtt_read` | 读取 RTT 数据 |
| `rtt_write` | 写入 RTT 数据 |
| `rtt_get_status` | 获取 RTT 状态 |

### SVD (5个)
| 工具 | 功能 |
|------|------|
| `list_svd_devices` | 列出 SVD 设备 |
| `get_svd_peripherals` | 获取外设列表 |
| `get_svd_registers` | 获取寄存器列表 |
| `read_register_with_fields` | 读取并解析寄存器 |
| `parse_register_value` | 解析寄存器值 |

### GDB Server (3个)
| 工具 | 功能 |
|------|------|
| `start_gdb_server` | 启动 GDB Server |
| `stop_gdb_server` | 停止 GDB Server |
| `get_gdb_server_status` | 获取 GDB Server 状态 |

### 指南工具 (4个)
| 工具 | 功能 |
|------|------|
| `get_usage_guidance` | 获取使用指南 |
| `get_best_practices` | 获取最佳实践 |
| `list_scenarios` | 列出使用场景 |
| `get_forbidden_operations` | 获取禁止操作列表 |

## 代码规范 / Code Conventions

### 注释格式

所有模块文档字符串采用中英文双语格式：

```python
"""Module Title in English / 中文模块标题.

Description in English.
中文描述。

Args:
    param: Parameter description / 参数描述

Returns:
    Return value description / 返回值描述
"""
```

### 命名规范

- 类名: PascalCase (如 `JLinkManager`)
- 函数名: snake_case (如 `connect_device`)
- 常量: UPPER_SNAKE_CASE (如 `CACHE_VERSION`)
- 私有成员: 前缀下划线 (如 `_instance`)

### 类型注解

所有公开函数必须有类型注解：

```python
def connect_device(
    serial_number: str | None = None,
    interface: str | None = None,
    chip_name: str | None = None
) -> Dict[str, Any]:
    ...
```

## 最佳实践 / Best Practices

### 读取寄存器流程

```python
# 1. 连接设备（支持芯片名称缩写）
connect_device(chip_name='FC7300F4MDD', interface='JTAG')

# 2. 暂停 CPU（必需！）
halt_cpu()

# 3. 读取寄存器
read_register_with_fields(device, peripheral, register)
```

### Flash 编程流程

```python
# 1. 连接设备
connect_device(chip_name='FC7300F4MDD')

# 2. 擦除 Flash
erase_flash(start_address=0x08000000, end_address=0x08020000)

# 3. 烧录并校验
program_flash(address=0x08000000, data=firmware_data, verify=True)
```

## 禁止操作 / Forbidden Operations

1. **不要**使用 `read_file` 工具读取 `src/jlink_mcp/` 下的源代码
2. **不要**在正常业务流程中插入源码分析或调试
3. **不要**重复调用已失败的连接（先分析错误）
4. **不要**调用 `get_svd_peripherals` 遍历所有外设来查找地址
5. **不要**跳过 `halt_cpu()` 步骤（读取寄存器/内存前必须暂停 CPU）

## 环境变量 / Environment Variables

| 变量 | 说明 |
|------|------|
| `JLINK_SVD_DIR` | 外部 SVD 文件目录 |
| `JLINK_PATCH_DIR` | 外部设备补丁目录 |

## 测试标记 / Test Markers

```bash
pytest -m unit          # 单元测试（无硬件依赖）
pytest -m integration   # 集成测试（需要硬件）
pytest -m mock          # Mock 测试
pytest -m performance   # 性能测试
pytest -m benchmark     # 基准测试
```

## 版本信息 / Version Info

- 当前版本: 0.1.1
- Python 要求: >=3.10
- 许可证: MIT
