# JLink MCP Server

[English](#english) | [中文](#中文)

---

## English

A Model Context Protocol (MCP) server for J-Link debuggers, providing comprehensive debugging capabilities through AI assistant integration.

### Features

- **Device Connection**: Connect to J-Link debuggers via SWD/JTAG interfaces
- **Memory Operations**: Read/write memory with configurable access widths
- **Flash Programming**: Program and verify flash memory
- **Debug Control**: Halt, run, step through execution
- **Register Access**: Read/write CPU registers
- **RTT Support**: Real-time data transfer via Segger RTT
- **SVD Integration**: Access peripheral registers via SVD files
- **Plugin Architecture**: Extensible device-specific patch system

### Installation

#### Prerequisites

- Python 3.8+
- J-Link software installed
- J-Link debugger hardware

#### Install from PyPI

```bash
pip install jlink-mcp
```

#### Install from Source

```bash
git clone https://github.com/cyj0920/jlink_mcp.git
cd jlink_mcp
pip install -e .
```

### Configuration

#### Environment Variables

```bash
# Optional: External SVD directory
export JLINK_SVD_DIR="/path/to/svd/files"

# Optional: External device patch directory
export JLINK_PATCH_DIR="/path/to/patches"
```

#### MCP Configuration

Add to your MCP configuration (e.g., `~/.config/mcp/settings.json`):

```json
{
  "mcpServers": {
    "jlink": {
      "command": "python",
      "args": ["-m", "jlink_mcp"],
      "env": {
        "JLINK_SVD_DIR": "/path/to/svd/files",
        "JLINK_PATCH_DIR": "/path/to/patches"
      }
    }
  }
}
```

### Usage

#### Connect to Device

```python
# Connect to device with automatic chip detection
connect_device(chip_name="auto", interface="JTAG")

# Connect with specific chip name
connect_device(chip_name="STM32F407VG", interface="SWD")
```

#### Memory Operations

```python
# Read memory
read_memory(address=0x20000000, size=64, width=32)

# Write memory
write_memory(address=0x20000000, data="0x12345678", width=32)
```

#### Flash Programming

```python
# Erase flash
erase_flash(start_address=0x08000000, end_address=0x08020000)

# Program flash
program_flash(address=0x08000000, data="binary_data", verify=True)
```

#### Debug Control

```python
# Halt CPU
halt_cpu()

# Run CPU
run_cpu()

# Single step
step_instruction()
```

#### Register Access

```python
# Read registers
read_registers()

# Read specific register
read_register(register_name="R0")

# Write register
write_register(register_name="R0", value=0x12345678)
```

#### SVD Register Access

```python
# List SVD peripherals
get_svd_peripherals(device_name="STM32F407VG")

# Get peripheral registers
get_svd_registers(device_name="STM32F407VG", peripheral_name="GPIOA")

# Read register with field parsing
read_register_with_fields(device_name="STM32F407VG", peripheral_name="GPIOA", register_name="MODER")
```

### Architecture

The server is built with a plugin architecture:

- **Device Patch Interface**: Abstract base for device-specific patches
- **Device Patch Manager**: Manages multiple patch plugins
- **SVD Manager**: Handles System View Description files
- **J-Link Manager**: Core J-Link connection management

This design allows for easy extension with new device support.

### Plugin System

Create custom device patches by implementing the `DevicePatchInterface`:

```python
from jlink_mcp.device_patch_interface import DevicePatchInterface

class CustomPatch(DevicePatchInterface):
    @property
    def vendor_name(self) -> str:
        return "CustomVendor"
    
    @property
    def patch_version(self) -> str:
        return "v1.0"
    
    def match_device_name(self, chip_name: str) -> Optional[str]:
        # Implement device name matching logic
        return matched_name
    
    @property
    def device_names(self) -> List[str]:
        # Return list of supported devices
        return ["CustomDevice1", "CustomDevice2"]
```

### License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 中文

一个用于J-Link调试器的模型上下文协议（MCP）服务器，通过AI助手集成提供全面的调试功能。

### 功能特性

- **设备连接**：通过SWD/JTAG接口连接J-Link调试器
- **内存操作**：支持可配置访问宽度的内存读写
- **Flash编程**：程序烧录和验证
- **调试控制**：暂停、运行、单步执行
- **寄存器访问**：读写CPU寄存器
- **RTT支持**：通过Segger RTT进行实时数据传输
- **SVD集成**：通过SVD文件访问外设寄存器
- **插件架构**：可扩展的设备特定补丁系统

### 安装

#### 前置要求

- Python 3.8+
- 已安装J-Link软件
- J-Link调试器硬件

#### 从PyPI安装

```bash
pip install jlink-mcp
```

#### 从源码安装

```bash
git clone https://github.com/cyj0920/jlink_mcp.git
cd jlink_mcp
pip install -e .
```

### 配置

#### 环境变量

```bash
# 可选：外部SVD目录
export JLINK_SVD_DIR="/path/to/svd/files"

# 可选：外部设备补丁目录
export JLINK_PATCH_DIR="/path/to/patches"
```

#### MCP配置

添加到你的MCP配置（例如 `~/.config/mcp/settings.json`）：

```json
{
  "mcpServers": {
    "jlink": {
      "command": "python",
      "args": ["-m", "jlink_mcp"],
      "env": {
        "JLINK_SVD_DIR": "/path/to/svd/files",
        "JLINK_PATCH_DIR": "/path/to/patches"
      }
    }
  }
}
```

### 使用方法

#### 连接设备

```python
# 自动检测芯片连接
connect_device(chip_name="auto", interface="JTAG")

# 指定芯片名称连接
connect_device(chip_name="STM32F407VG", interface="SWD")
```

#### 内存操作

```python
# 读取内存
read_memory(address=0x20000000, size=64, width=32)

# 写入内存
write_memory(address=0x20000000, data="0x12345678", width=32)
```

#### Flash编程

```python
# 擦除Flash
erase_flash(start_address=0x08000000, end_address=0x08020000)

# 烧录Flash
program_flash(address=0x08000000, data="binary_data", verify=True)
```

#### 调试控制

```python
# 暂停CPU
halt_cpu()

# 运行CPU
run_cpu()

# 单步执行
step_instruction()
```

#### 寄存器访问

```python
# 读取寄存器
read_registers()

# 读取特定寄存器
read_register(register_name="R0")

# 写入寄存器
write_register(register_name="R0", value=0x12345678)
```

#### SVD寄存器访问

```python
# 列出SVD外设
get_svd_peripherals(device_name="STM32F407VG")

# 获取外设寄存器
get_svd_registers(device_name="STM32F407VG", peripheral_name="GPIOA")

# 读取寄存器并解析字段
read_register_with_fields(device_name="STM32F407VG", peripheral_name="GPIOA", register_name="MODER")
```

### 架构

服务器采用插件架构构建：

- **设备补丁接口**：设备特定补丁的抽象基类
- **设备补丁管理器**：管理多个补丁插件
- **SVD管理器**：处理系统视图描述文件
- **J-Link管理器**：核心J-Link连接管理

这种设计允许轻松扩展以支持新设备。

### 插件系统

通过实现 `DevicePatchInterface` 创建自定义设备补丁：

```python
from jlink_mcp.device_patch_interface import DevicePatchInterface

class CustomPatch(DevicePatchInterface):
    @property
    def vendor_name(self) -> str:
        return "CustomVendor"
    
    @property
    def patch_version(self) -> str:
        return "v1.0"
    
    def match_device_name(self, chip_name: str) -> Optional[str]:
        # 实现设备名称匹配逻辑
        return matched_name
    
    @property
    def device_names(self) -> List[str]:
        # 返回支持的设备列表
        return ["CustomDevice1", "CustomDevice2"]
```

### 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件。

### 贡献

欢迎贡献！请随时提交Pull Request。