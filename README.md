<div align="center">

# JLink MCP Server

**A powerful Model Context Protocol (MCP) server for J-Link debuggers**

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI Version](https://badge.fury.io/py/jlink-mcp.svg)](https://pypi.org/project/jlink-mcp/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

**J-Link调试器的强大模型上下文协议（MCP）服务器**

[![Python版本](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PyPI版本](https://badge.fury.io/py/jlink-mcp.svg)](https://pypi.org/project/jlink-mcp/)
[![许可证](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![MCP](https://img.shields.io/badge/MCP-Compatible-orange.svg)](https://modelcontextprotocol.io/)

---

[English](#english-documentation) | [中文文档](#中文文档)

</div>

---

## English Documentation

### 🚀 Overview

JLink MCP Server is a comprehensive debugging tool that integrates J-Link debugger capabilities with AI assistants through the Model Context Protocol. It provides seamless access to hardware debugging features including memory operations, flash programming, register access, and real-time data transfer.

### ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🔌 **Device Connection** | Connect via SWD/JTAG with automatic chip detection |
| 🔍 **Smart Chip Matching** | Intelligent chip name matching (e.g., `FC7300F4MDD` → `FC7300F4MDDxXxxxT1C`) |
| 💾 **Memory Operations** | Read/write memory with configurable access widths (8/16/32-bit) |
| 🔥 **Flash Programming** | Program, erase, and verify flash memory |
| 🎯 **Debug Control** | Halt, run, single-step execution with breakpoints |
| 📊 **Register Access** | Read/write CPU registers with SVD field parsing |
| 📡 **RTT Support** | Real-time data transfer via Segger RTT |
| 🔧 **SVD Integration** | Access peripheral registers via SVD files with pickle cache |
| 🧩 **Plugin Architecture** | Extensible device-specific patch system |
| 🌐 **GDB Server** | Integrated GDB server support |
| 📚 **Usage Guidance** | Built-in help tools for best practices and scenarios |

### 📋 Prerequisites

- **Python**: 3.8 or higher
- **J-Link Software**: Latest version from [Segger](https://www.segger.com/downloads/jlink/)
- **J-Link Hardware**: Any supported J-Link debugger
- **Operating System**: Windows, Linux, or macOS

### 🛠️ Installation

#### Method 1: Install from PyPI

```bash
pip install jlink-mcp
```

#### Method 2: Install from Source

```bash
# Clone the repository
git clone https://github.com/cyj0920/jlink_mcp.git
cd jlink_mcp

# Install in development mode
pip install -e .
```

#### Method 3: Install with UV (Recommended for better performance)

```bash
# Install UV
pip install uv

# Install with UV
uv pip install jlink-mcp
```

### ⚙️ Configuration

#### Environment Variables

Create a `.env` file or set environment variables:

```bash
# Optional: External SVD directory for peripheral register definitions
JLINK_SVD_DIR=/path/to/svd/files

# Optional: External device patch directory for vendor-specific support
JLINK_PATCH_DIR=/path/to/patches

# Optional: Default interface type (SWD or JTAG)
JLINK_DEFAULT_INTERFACE=JTAG
```

#### MCP Configuration

Add to your MCP configuration file (typically `~/.config/mcp/settings.json` or `C:\Users\<username>\.iflow\settings.json`):

```json
{
  "mcpServers": {
    "jlink": {
      "command": "python",
      "args": ["-m", "jlink_mcp"],
      "env": {
        "JLINK_SVD_DIR": "C:\\path\\to\\svd\\files",
        "JLINK_PATCH_DIR": "C:\\path\\to\\patches",
        "JLINK_DEFAULT_INTERFACE": "JTAG"
      }
    }
  }
}
```

### 📖 Usage Guide

#### Connecting to Devices

<details>
<summary>📂 Expand: Connection Examples</summary>

```python
# Automatic chip detection (recommended)
connect_device(chip_name="auto", interface="JTAG")

# Connect with specific chip name
connect_device(chip_name="STM32F407VG", interface="SWD")

# Connect with specific J-Link serial number
connect_device(
    chip_name="STM32F407VG",
    interface="JTAG",
    serial_number="12345678"
)
```

</details>

#### Memory Operations

<details>
<summary>📂 Expand: Memory Read/Write Examples</summary>

```python
# Read 64 bytes from address 0x20000000 (32-bit access)
read_memory(address=0x20000000, size=64, width=32)

# Write a 32-bit value to memory
write_memory(address=0x20000000, data="0x12345678", width=32)

# Read a single byte
read_memory(address=0x20000000, size=1, width=8)

# Write 16-bit value
write_memory(address=0x20000000, data="0xABCD", width=16)
```

</details>

#### Flash Programming

<details>
<summary>📂 Expand: Flash Operation Examples</summary>

```python
# Erase a range of flash memory
erase_flash(
    start_address=0x08000000,
    end_address=0x08020000
)

# Erase entire chip
erase_flash(chip_erase=True)

# Program flash with verification
program_flash(
    address=0x08000000,
    data="binary_hex_data",
    verify=True
)

# Verify flash content
verify_flash(
    address=0x08000000,
    data="expected_data"
)
```

</details>

#### Debug Control

<details>
<summary>📂 Expand: Debug Control Examples</summary>

```python
# Halt the CPU
halt_cpu()

# Resume execution
run_cpu()

# Single step execution
step_instruction()

# Get current CPU state
get_cpu_state()

# Reset the device
reset_target(reset_type="normal")

# Reset and halt
reset_target(reset_type="halt")
```

</details>

#### Register Access

<details>
<summary>📂 Expand: Register Access Examples</summary>

```python
# Read all general-purpose registers
read_registers()

# Read specific registers
read_registers(register_names=["R0", "R1", "PC"])

# Write to a register
write_register(register_name="R0", value=0x12345678)

# Read with custom list
read_registers(["R0", "SP", "LR", "PC"])
```

</details>

#### SVD Register Access

<details>
<summary>📂 Expand: SVD Examples</summary>

```python
# List available SVD files
list_svd_devices()

# Get peripherals for a device
get_svd_peripherals(device_name="STM32F407VG")

# Get registers for a peripheral
get_svd_registers(
    device_name="STM32F407VG",
    peripheral_name="GPIOA"
)

# Read register with field parsing
result = read_register_with_fields(
    device_name="STM32F407VG",
    peripheral_name="GPIOA",
    register_name="MODER"
)
print(f"Raw value: {result['value']}")
print(f"Fields: {result['fields']}")
```

</details>

#### Breakpoints and Debugging

<details>
<summary>📂 Expand: Breakpoint Examples</summary>

```python
# Set a breakpoint
set_breakpoint(address=0x08000100)

# Clear a breakpoint
clear_breakpoint(address=0x08000100)
```

</details>

#### RTT (Real-Time Transfer)

<details>
<summary>📂 Expand: RTT Examples</summary>

```python
# Start RTT with buffer index 0
rtt_start(buffer_index=0)

# Read RTT data
data = rtt_read(buffer_index=0, size=1024)
print(data)

# Write data to RTT
rtt_write(data="test_message", buffer_index=0)

# Stop RTT
rtt_stop()

# Get RTT status
status = rtt_get_status()
```

</details>

### 🏗️ Architecture

The server follows a modular, plugin-based architecture:

```
┌─────────────────────────────────────────────────┐
│           JLink MCP Server                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌────────────────────┐     │
│  │   Server     │  │   Tool Layer       │     │
│  │   Manager    │  │                    │     │
│  └──────┬───────┘  │  • Connection      │     │
│         │          │  • Debug           │     │
│         │          │  • Memory          │     │
│         │          │  • Flash           │     │
│         │          │  • Registers       │     │
│         │          │  • SVD             │     │
│         │          │  • RTT             │     │
│         │          └────────────────────┘     │
│         │                                        │
│  ┌──────▼────────────────────────────────┐      │
│  │         Manager Layer                  │      │
│  ├────────────┬────────────┬─────────────┤      │
│  │ JLink      │ SVD        │ Patch       │      │
│  │ Manager    │ Manager    │ Manager     │      │
│  └────────────┴────────────┴─────────────┘      │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │         Plugin Layer                      │   │
│  │  • DevicePatchInterface                  │   │
│  │  • Vendor-specific patches               │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │         Hardware Layer                    │   │
│  │  • pylink-square                          │   │
│  │  • J-Link SDK                            │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 🧩 Plugin System

The server supports a flexible plugin architecture for device-specific functionality:

#### Creating a Custom Patch

```python
from typing import Optional, List, Dict, Any
from jlink_mcp.device_patch_interface import DevicePatchInterface

class CustomDevicePatch(DevicePatchInterface):
    """Custom device patch implementation."""

    @property
    def vendor_name(self) -> str:
        """Return the vendor name."""
        return "CustomVendor"

    @property
    def patch_version(self) -> str:
        """Return the patch version."""
        return "v1.0.0"

    def is_available(self) -> bool:
        """Check if the patch is available."""
        return True

    def match_device_name(self, chip_name: str) -> Optional[str]:
        """
        Match and return the full device name.

        Args:
            chip_name: Partial or simplified device name

        Returns:
            Full device name or None if no match
        """
        # Implement your matching logic
        device_map = {
            "CUSTOM": "CustomDevice1",
            "CUST1": "CustomDevice1",
        }
        return device_map.get(chip_name.upper())

    @property
    def device_names(self) -> List[str]:
        """Return list of supported devices."""
        return ["CustomDevice1", "CustomDevice2"]

    def get_device_info(self, device_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a device.

        Args:
            device_name: Full device name

        Returns:
            Device information dictionary
        """
        return {
            "name": device_name,
            "vendor": self.vendor_name,
            "core": "ARM Cortex-M4",
            "flash_size": 512 * 1024,
            "ram_size": 128 * 1024,
        }
```

#### Registering a Custom Patch

```python
from jlink_mcp.device_patch_manager import device_patch_manager

# Create and register your custom patch
custom_patch = CustomDevicePatch()
device_patch_manager.register_patch(custom_patch)
```

### 📚 API Reference

The server provides **41 MCP tools** across 9 categories:

#### Connection API (5 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `list_jlink_devices` | - | List connected J-Link devices |
| `connect_device` | `serial_number?`, `interface?`, `chip_name?` | Connect to J-Link device |
| `disconnect_device` | - | Disconnect from current device |
| `get_connection_status` | - | Get connection status |
| `match_chip_name` | `chip_name` | Smart chip name matching |

#### Device Info API (4 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `get_target_info` | - | Get target device information |
| `get_target_voltage` | - | Get target voltage |
| `scan_target_devices` | - | Scan for devices on the bus |
| `list_device_patches` | - | List loaded device patches |

#### Memory API (4 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `read_memory` | `address`, `size`, `width?` | Read memory (max 64KB) |
| `write_memory` | `address`, `data`, `width?` | Write memory |
| `read_registers` | `register_names?` | Read CPU registers |
| `write_register` | `register_name`, `value` | Write single register |

#### Flash API (3 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `erase_flash` | `start_address?`, `end_address?`, `chip_erase?` | Erase flash |
| `program_flash` | `address`, `data`, `verify?` | Program flash |
| `verify_flash` | `address`, `data` | Verify flash |

#### Debug API (7 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `reset_target` | `reset_type?` | Reset target (normal/halt/core) |
| `halt_cpu` | - | Halt CPU |
| `run_cpu` | - | Run CPU |
| `step_instruction` | - | Single step execution |
| `get_cpu_state` | - | Get CPU state |
| `set_breakpoint` | `address` | Set breakpoint |
| `clear_breakpoint` | `address` | Clear breakpoint |

#### RTT API (5 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `rtt_start` | `buffer_index?`, `read_mode?`, `timeout_ms?` | Start RTT |
| `rtt_stop` | - | Stop RTT |
| `rtt_read` | `buffer_index?`, `size?`, `timeout_ms?` | Read RTT data |
| `rtt_write` | `data`, `buffer_index?` | Write RTT data |
| `rtt_get_status` | - | Get RTT status |

#### GDB Server API (3 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `start_gdb_server` | `host?`, `port?`, `device?`, `interface?`, `speed?` | Start GDB server |
| `stop_gdb_server` | - | Stop GDB server |
| `get_gdb_server_status` | - | Get GDB server status |

#### SVD API (5 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `list_svd_devices` | - | List available SVD devices |
| `get_svd_peripherals` | `device_name` | Get device peripherals |
| `get_svd_registers` | `device_name`, `peripheral_name` | Get peripheral registers |
| `read_register_with_fields` | `device_name`, `peripheral_name`, `register_name` | Read register with field parsing |
| `parse_register_value` | `device_name`, `peripheral_name`, `register_name`, `value` | Parse register value only |

#### Guidance API (5 tools)

| Function | Parameters | Description |
|----------|------------|-------------|
| `get_usage_guidance` | `category?`, `include_examples?` | Get tool usage guide |
| `get_best_practices` | `task_type` | Get best practices |
| `list_scenarios` | - | List usage scenarios |
| `get_forbidden_operations` | - | Get forbidden operations |
| `get_system_prompt` | `prompt_name?` | Get system/custom prompt |

### 🐛 Troubleshooting

#### Common Issues

<details>
<summary>📂 Connection Issues</summary>

**Problem**: Cannot connect to J-Link device

**Solutions**:
1. Check if J-Link is properly connected via USB
2. Verify J-Link software is installed
3. Try running JLinkExe to verify device detection
4. Check interface type (SWD vs JTAG)
5. Verify target device is powered

```bash
# Test J-Link connection
JLinkExe -device STM32F407VG -if JTAG -speed 4000
```

</details>

<details>
<summary>📂 Memory Access Issues</summary>

**Problem**: Memory read/write fails

**Solutions**:
1. Verify target is halted before memory access
2. Check memory address is valid and accessible
3. Ensure correct access width for target memory region
4. Verify target is powered and not in low-power mode

</details>

<details>
<summary>📂 Flash Programming Issues</summary>

**Problem**: Flash programming fails

**Solutions**:
1. Erase flash before programming
2. Verify target device is not write-protected
3. Check flash algorithm matches target device
4. Ensure sufficient power supply during programming

</details>

### 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- [Segger](https://www.segger.com/) for J-Link hardware and software
- [pylink-square](https://github.com/blacksphere/pylink-square) for the Python J-Link library
- [Model Context Protocol](https://modelcontextprotocol.io/) for the MCP specification

---

## 中文文档

### 🚀 概述

JLink MCP Server 是一个功能强大的调试工具，通过模型上下文协议将J-Link调试器功能与AI助手集成。它提供无缝的硬件调试功能访问，包括内存操作、Flash编程、寄存器访问和实时数据传输。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🔌 **设备连接** | 通过SWD/JTAG连接，支持自动芯片检测 |
| 🔍 **智能芯片匹配** | 智能芯片名称匹配（如 `FC7300F4MDD` → `FC7300F4MDDxXxxxT1C`） |
| 💾 **内存操作** | 支持可配置访问宽度（8/16/32位）的内存读写 |
| 🔥 **Flash编程** | 程序烧录、擦除和验证 |
| 🎯 **调试控制** | 暂停、运行、单步执行及断点设置 |
| 📊 **寄存器访问** | 读写CPU寄存器，支持SVD字段解析 |
| 📡 **RTT支持** | 通过Segger RTT进行实时数据传输 |
| 🔧 **SVD集成** | 通过SVD文件访问外设寄存器，支持Pickle缓存 |
| 🧩 **插件架构** | 可扩展的设备特定补丁系统 |
| 🌐 **GDB服务器** | 集成GDB服务器支持 |
| 📚 **使用指南** | 内置帮助工具，提供最佳实践和使用场景 |

### 📋 前置要求

- **Python**: 3.8 或更高版本
- **J-Link软件**: 从 [Segger](https://www.segger.com/downloads/jlink/) 获取最新版本
- **J-Link硬件**: 任何支持的J-Link调试器
- **操作系统**: Windows、Linux 或 macOS

### 🛠️ 安装

#### 方法1：从PyPI安装

```bash
pip install jlink-mcp
```

#### 方法2：从源码安装

```bash
# 克隆仓库
git clone https://github.com/cyj0920/jlink_mcp.git
cd jlink_mcp

# 开发模式安装
pip install -e .
```

#### 方法3：使用UV安装（推荐，性能更好）

```bash
# 安装UV
pip install uv

# 使用UV安装
uv pip install jlink-mcp
```

### ⚙️ 配置

#### 环境变量

创建 `.env` 文件或设置环境变量：

```bash
# 可选：外部SVD目录，用于外设寄存器定义
JLINK_SVD_DIR=/path/to/svd/files

# 可选：外部设备补丁目录，用于厂商特定支持
JLINK_PATCH_DIR=/path/to/patches

# 可选：默认接口类型（SWD或JTAG）
JLINK_DEFAULT_INTERFACE=JTAG
```

#### MCP配置

添加到你的MCP配置文件（通常在 `~/.config/mcp/settings.json` 或 `C:\Users\<用户名>\.iflow\settings.json`）：

```json
{
  "mcpServers": {
    "jlink": {
      "command": "python",
      "args": ["-m", "jlink_mcp"],
      "env": {
        "JLINK_SVD_DIR": "C:\\path\\to\\svd\\files",
        "JLINK_PATCH_DIR": "C:\\path\\to\\patches",
        "JLINK_DEFAULT_INTERFACE": "JTAG"
      }
    }
  }
}
```

### 📖 使用指南

#### 连接设备

<details>
<summary>📂 展开：连接示例</summary>

```python
# 自动芯片检测（推荐）
connect_device(chip_name="auto", interface="JTAG")

# 指定芯片名称连接
connect_device(chip_name="STM32F407VG", interface="SWD")

# 使用特定J-Link序列号连接
connect_device(
    chip_name="STM32F407VG",
    interface="JTAG",
    serial_number="12345678"
)
```

</details>

#### 内存操作

<details>
<summary>📂 展开：内存读写示例</summary>

```python
# 从地址0x20000000读取64字节（32位访问）
read_memory(address=0x20000000, size=64, width=32)

# 向内存写入32位值
write_memory(address=0x20000000, data="0x12345678", width=32)

# 读取单个字节
read_memory(address=0x20000000, size=1, width=8)

# 写入16位值
write_memory(address=0x20000000, data="0xABCD", width=16)
```

</details>

#### Flash编程

<details>
<summary>📂 展开：Flash操作示例</summary>

```python
# 擦除Flash的一个区域
erase_flash(
    start_address=0x08000000,
    end_address=0x08020000
)

# 擦除整个芯片
erase_flash(chip_erase=True)

# 烧录Flash并验证
program_flash(
    address=0x08000000,
    data="binary_hex_data",
    verify=True
)

# 验证Flash内容
verify_flash(
    address=0x08000000,
    data="expected_data"
)
```

</details>

#### 调试控制

<details>
<summary>📂 展开：调试控制示例</summary>

```python
# 暂停CPU
halt_cpu()

# 恢复执行
run_cpu()

# 单步执行
step_instruction()

# 获取当前CPU状态
get_cpu_state()

# 复位设备
reset_target(reset_type="normal")

# 复位并暂停
reset_target(reset_type="halt")
```

</details>

#### 寄存器访问

<details>
<summary>📂 展开：寄存器访问示例</summary>

```python
# 读取所有通用寄存器
read_registers()

# 读取特定寄存器
read_registers(register_names=["R0", "R1", "PC"])

# 写入寄存器
write_register(register_name="R0", value=0x12345678)

# 使用自定义列表读取
read_registers(["R0", "SP", "LR", "PC"])
```

</details>

#### SVD寄存器访问

<details>
<summary>📂 展开：SVD示例</summary>

```python
# 列出可用的SVD文件
list_svd_devices()

# 获取设备的外设
get_svd_peripherals(device_name="STM32F407VG")

# 获取外设的寄存器
get_svd_registers(
    device_name="STM32F407VG",
    peripheral_name="GPIOA"
)

# 读取寄存器并解析字段
result = read_register_with_fields(
    device_name="STM32F407VG",
    peripheral_name="GPIOA",
    register_name="MODER"
)
print(f"原始值: {result['value']}")
print(f"字段: {result['fields']}")
```

</details>

#### 断点和调试

<details>
<summary>📂 展开：断点示例</summary>

```python
# 设置断点
set_breakpoint(address=0x08000100)

# 清除断点
clear_breakpoint(address=0x08000100)
```

</details>

#### RTT（实时传输）

<details>
<summary>📂 展开：RTT示例</summary>

```python
# 启动RTT，使用缓冲区索引0
rtt_start(buffer_index=0)

# 读取RTT数据
data = rtt_read(buffer_index=0, size=1024)
print(data)

# 向RTT写入数据
rtt_write(data="test_message", buffer_index=0)

# 停止RTT
rtt_stop()

# 获取RTT状态
status = rtt_get_status()
```

</details>

### 🏗️ 架构

服务器采用模块化、基于插件的架构：

```
┌─────────────────────────────────────────────────┐
│           JLink MCP Server                       │
├─────────────────────────────────────────────────┤
│                                                 │
│  ┌──────────────┐  ┌────────────────────┐     │
│  │   Server     │  │   工具层           │     │
│  │   Manager    │  │                    │     │
│  └──────┬───────┘  │  • 连接            │     │
│         │          │  • 调试            │     │
│         │          │  • 内存            │     │
│         │          │  • Flash           │     │
│         │          │  • 寄存器          │     │
│         │          │  • SVD             │     │
│         │          │  • RTT             │     │
│         │          └────────────────────┘     │
│         │                                        │
│  ┌──────▼────────────────────────────────┐      │
│  │         管理器层                        │      │
│  ├────────────┬────────────┬─────────────┤      │
│  │ JLink      │ SVD        │ 补丁        │      │
│  │ 管理器     │ 管理器     │ 管理器      │      │
│  └────────────┴────────────┴─────────────┘      │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │         插件层                           │   │
│  │  • DevicePatchInterface                  │   │
│  │  • 厂商特定补丁                          │   │
│  └──────────────────────────────────────────┘   │
│                                                 │
│  ┌──────────────────────────────────────────┐   │
│  │         硬件层                           │   │
│  │  • pylink-square                          │   │
│  │  • J-Link SDK                            │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### 🧩 插件系统

服务器支持灵活的插件架构，用于设备特定功能：

#### 创建自定义补丁

```python
from typing import Optional, List, Dict, Any
from jlink_mcp.device_patch_interface import DevicePatchInterface

class CustomDevicePatch(DevicePatchInterface):
    """自定义设备补丁实现。"""

    @property
    def vendor_name(self) -> str:
        """返回厂商名称。"""
        return "CustomVendor"

    @property
    def patch_version(self) -> str:
        """返回补丁版本。"""
        return "v1.0.0"

    def is_available(self) -> bool:
        """检查补丁是否可用。"""
        return True

    def match_device_name(self, chip_name: str) -> Optional[str]:
        """
        匹配并返回完整的设备名称。

        Args:
            chip_name: 部分或简化的设备名称

        Returns:
            完整的设备名称或None（如果不匹配）
        """
        # 实现你的匹配逻辑
        device_map = {
            "CUSTOM": "CustomDevice1",
            "CUST1": "CustomDevice1",
        }
        return device_map.get(chip_name.upper())

    @property
    def device_names(self) -> List[str]:
        """返回支持的设备列表。"""
        return ["CustomDevice1", "CustomDevice2"]

    def get_device_info(self, device_name: str) -> Optional[Dict[str, Any]]:
        """
        获取设备的详细信息。

        Args:
            device_name: 完整的设备名称

        Returns:
            设备信息字典
        """
        return {
            "name": device_name,
            "vendor": self.vendor_name,
            "core": "ARM Cortex-M4",
            "flash_size": 512 * 1024,
            "ram_size": 128 * 1024,
        }
```

#### 注册自定义补丁

```python
from jlink_mcp.device_patch_manager import device_patch_manager

# 创建并注册你的自定义补丁
custom_patch = CustomDevicePatch()
device_patch_manager.register_patch(custom_patch)
```

### 📚 API参考

#### 核心函数

<details>
<summary>📂 展开：连接API</summary>

| 函数 | 参数 | 描述 |
|------|------|------|
| `connect_device` | `chip_name`, `interface`, `serial_number` | 连接到J-Link设备 |
| `disconnect_device` | - | 断开当前设备连接 |
| `get_connection_status` | - | 获取连接状态 |
| `list_jlink_devices` | - | 列出连接的J-Link设备 |
| `scan_target_devices` | - | 扫描总线上的设备 |
| `get_target_info` | - | 获取目标设备信息 |
| `get_target_voltage` | - | 获取目标电压 |

</details>

<details>
<summary>📂 展开：内存API</summary>

| 函数 | 参数 | 描述 |
|------|------|------|
| `read_memory` | `address`, `size`, `width` | 读取内存 |
| `write_memory` | `address`, `data`, `width` | 写入内存 |

</details>

<details>
<summary>📂 展开：Flash API</summary>

| 函数 | 参数 | 描述 |
|------|------|------|
| `erase_flash` | `start_address`, `end_address`, `chip_erase` | 擦除Flash |
| `program_flash` | `address`, `data`, `verify` | 烧录Flash |
| `verify_flash` | `address`, `data` | 验证Flash |

</details>

<details>
<summary>📂 展开：调试API</summary>

| 函数 | 参数 | 描述 |
|------|------|------|
| `reset_target` | `reset_type` | 复位目标 |
| `halt_cpu` | - | 暂停CPU |
| `run_cpu` | - | 运行CPU |
| `step_instruction` | - | 单步执行 |
| `get_cpu_state` | - | 获取CPU状态 |
| `set_breakpoint` | `address` | 设置断点 |
| `clear_breakpoint` | `address` | 清除断点 |

</details>

### 🐛 故障排除

#### 常见问题

<details>
<summary>📂 连接问题</summary>

**问题**: 无法连接到J-Link设备

**解决方案**:
1. 检查J-Link是否通过USB正确连接
2. 验证J-Link软件已安装
3. 尝试运行JLinkExe验证设备检测
4. 检查接口类型（SWD vs JTAG）
5. 验证目标设备已上电

```bash
# 测试J-Link连接
JLinkExe -device STM32F407VG -if JTAG -speed 4000
```

</details>

<details>
<summary>📂 内存访问问题</summary>

**问题**: 内存读写失败

**解决方案**:
1. 内存访问前确保目标已暂停
2. 检查内存地址有效且可访问
3. 确保目标内存区域使用正确的访问宽度
4. 验证目标已上电且未处于低功耗模式

</details>

<details>
<summary>📂 Flash编程问题</summary>

**问题**: Flash编程失败

**解决方案**:
1. 编程前擦除Flash
2. 验证目标设备未写保护
3. 检查Flash算法与目标设备匹配
4. 确保编程期间有足够的电源供应

</details>

### 🤝 贡献

欢迎贡献！请遵循以下准则：

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 📝 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- [Segger](https://www.segger.com/) 提供J-Link硬件和软件
- [pylink-square](https://github.com/blacksphere/pylink-square) 提供Python J-Link库
- [Model Context Protocol](https://modelcontextprotocol.io/) 提供MCP规范

---

<div align="center">

**Made with ❤️ for the embedded development community**

**为嵌入式开发社区用❤️打造**

</div>