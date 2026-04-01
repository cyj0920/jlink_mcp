# JLink MCP API 文档

## 概述

JLink MCP 服务器提供 **46 个工具**，用于与 JLink 调试器和目标芯片交互。

### 统一返回格式

所有工具返回 JSON 格式，遵循以下结构：

**成功响应**：
```json
{
  "success": true,
  "data": { ... },      // 具体数据
  "message": "操作说明"
}
```

**失败响应**：
```json
{
  "success": false,
  "error": {
    "code": 101,
    "description": "错误描述",
    "detail": "详细信息",
    "suggestion": "修复建议"
  }
}
```

### 数据类型说明

| 类型 | 说明 | 示例 |
|------|------|------|
| `int` | 整数，地址或数值 | `0x20000000`, `65536` |
| `string` | 字符串 | `"FC7300F4MDD"` |
| `bytes` | 二进制数据 | `b'\x12\x34\x56\x78'` |
| `list` | 列表 | `["R0", "PC"]` |
| `bool` | 布尔值 | `true`, `false` |

### 工具依赖关系

部分工具需要在特定状态下调用：

```
连接状态依赖：
├── 未连接时可调用：
│   ├── list_jlink_devices
│   └── match_chip_name
│
├── 需要连接后调用：
│   ├── get_target_info
│   ├── get_target_voltage
│   ├── read_memory / write_memory
│   ├── read_registers / write_register
│   ├── erase_flash / program_flash / verify_flash
│   ├── reset_target / halt_cpu / run_cpu
│   ├── set_breakpoint / clear_breakpoint
│   ├── rtt_* 系列工具
│   └── gdb_* 系列工具
│
└── SVD 工具（独立）：
    ├── list_svd_devices
    ├── get_svd_peripherals
    ├── get_svd_registers
    └── parse_register_value
        └── read_register_with_fields（需要连接）
```

---

## 连接管理 (5个)

### list_jlink_devices

列出所有连接的 JLink 设备。

**参数**: 无

**返回值**:
```json
[{
  "serial_number": "941000024",
  "product_name": "J-Link",
  "firmware_version": "V2.45",
  "connection_type": "USB"
}]
```

---

### connect_device

连接到 JLink 设备。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `serial_number` | string | 否 | 设备序列号，None 则连接第一个设备 |
| `interface` | string | 否 | 接口类型，默认 "JTAG"，可选 "SWD" |
| `chip_name` | string | 否 | 芯片名称，支持简化名称自动匹配 |

**返回值**:
```json
{
  "success": true,
  "serial_number": "941000024",
  "message": "成功连接到设备 941000024，接口: JTAG"
}
```

---

### disconnect_device

断开 JLink 设备连接。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "设备已断开连接"
}
```

---

### get_connection_status

获取当前连接状态。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "connected": true,
    "device_serial": "941000024",
    "target_interface": "JTAG",
    "target_voltage": 3.3,
    "target_connected": true,
    "firmware_version": "V2.45"
  }
}
```

---

### match_chip_name

智能匹配芯片名称。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `chip_name` | string | 是 | 芯片名称（支持简化名称） |

**返回值**:
```json
{
  "success": true,
  "input": "FC7300F4MDD",
  "matched": "FC7300F4MDDxXxxxT1C",
  "all_matches": ["FC7300F4MDDxXxxxT1C", "FC7300F4MDDxXxxxT1B"],
  "suggestion": "匹配成功: FC7300F4MDDxXxxxT1C (补丁: Flagchip)"
}
```

---

## 设备信息 (4个)

### get_target_info

获取目标设备信息。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "device_name": "FC4150F2MBSxXxxxT1A",
    "core_type": "Cortex-M4",
    "core_id": "0x6BA02477",
    "flash_size": 2097152,
    "ram_size": 196608
  }
}
```

---

### get_target_voltage

获取目标芯片供电电压。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "voltage_v": 3.3,
    "status": "normal"
  }
}
```

---

### scan_target_devices

扫描目标总线上的设备。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "device_count": 1,
  "devices": ["0x6BA02477"]
}
```

---

### list_device_patches

列出所有已加载的设备补丁。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "patch_count": 1,
  "patches": [{
    "vendor": "Flagchip",
    "version": "v2.45",
    "device_count": 57
  }]
}
```

---

## 内存操作 (4个)

### read_memory

读取指定地址的内存。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | int | 是 | 起始地址 |
| `size` | int | 是 | 读取大小（字节，最大 64KB） |
| `width` | int | 否 | 数据宽度，默认 32，可选 8/16/32 |

**返回值**:
```json
{
  "success": true,
  "data": [18, 52, 86, 120],
  "hex_dump": "12 34 56 78",
  "address": 536870912
}
```

---

### write_memory

写入内存。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | int | 是 | 起始地址 |
| `data` | bytes | 是 | 要写入的数据 |
| `width` | int | 否 | 数据宽度，默认 32 |

**返回值**:
```json
{
  "success": true,
  "bytes_written": 4,
  "message": "成功写入 4 字节到地址 0x20000000"
}
```

---

### read_registers

读取 CPU 寄存器。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `register_names` | list[string] | 否 | 寄存器名称列表，None 读取所有 |

**返回值**:
```json
{
  "success": true,
  "registers": [
    {"name": "R0", "value": 0},
    {"name": "R15 (PC)", "value": 134218752}
  ]
}
```

---

### write_register

写入单个寄存器。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `register_name` | string | 是 | 寄存器名称 |
| `value` | int | 是 | 寄存器值 |

**返回值**:
```json
{
  "success": true,
  "register_name": "R0",
  "value": 305419896,
  "message": "成功写入寄存器 R0 = 0x12345678"
}
```

---

## Flash 操作 (3个)

### erase_flash

擦除 Flash。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `start_address` | int | 否 | 起始地址 |
| `end_address` | int | 否 | 结束地址 |
| `chip_erase` | bool | 否 | 是否整片擦除，默认 false |

**返回值**:
```json
{
  "success": true,
  "erase_type": "chip",
  "bytes_erased": 0,
  "message": "Flash 擦除成功（chip）"
}
```

---

### program_flash

烧录固件到 Flash。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | int | 是 | 起始地址 |
| `data` | bytes | 是 | 要烧录的数据 |
| `verify` | bool | 否 | 烧录后是否校验，默认 true |

**返回值**:
```json
{
  "success": true,
  "bytes_programmed": 65536,
  "verify_result": {"matched": true, "mismatches": []},
  "message": "成功烧录 64 KB 到 Flash"
}
```

---

### verify_flash

校验 Flash 内容。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | int | 是 | 起始地址 |
| `data` | bytes | 是 | 期望的数据 |

**返回值**:
```json
{
  "success": true,
  "matched": true,
  "mismatches": [],
  "message": "Flash 校验成功"
}
```

---

## 调试控制 (7个)

### reset_target

复位目标芯片。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `reset_type` | string | 否 | 复位类型：normal/halt/core，默认 normal |

**返回值**:
```json
{
  "success": true,
  "reset_type": "normal",
  "message": "目标已复位（normal）"
}
```

---

### halt_cpu

暂停 CPU。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "pc": 134218752,
  "message": "CPU 已暂停，PC = 0x8000000"
}
```

---

### run_cpu

运行 CPU。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "CPU 已开始运行"
}
```

---

### step_instruction

单步执行一条指令。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "pc": 134218756,
  "message": "单步执行完成，PC = 0x8000004"
}
```

---

### get_cpu_state

获取 CPU 状态。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "running": false,
  "halted": true,
  "pc": 134218752,
  "lr": null,
  "sp": null,
  "message": "CPU 状态: 已暂停"
}
```

---

### set_breakpoint

设置断点。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | int | 是 | 断点地址 |

**返回值**:
```json
{
  "success": true,
  "address": 134218752,
  "message": "断点已设置: 0x8000000"
}
```

---

### clear_breakpoint

清除断点。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `address` | int | 是 | 断点地址 |

**返回值**:
```json
{
  "success": true,
  "address": 134218752,
  "message": "断点已清除: 0x8000000"
}
```

---

## RTT 工具 (5个)

### rtt_start

启动 RTT。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `buffer_index` | int | 否 | RTT 缓冲区索引，默认 0 |
| `read_mode` | string | 否 | 读取模式，默认 "continuous" |
| `timeout_ms` | int | 否 | 超时时间（毫秒），默认 1000 |

**返回值**:
```json
{
  "success": true,
  "buffer_index": 0,
  "message": "RTT 已启动（缓冲区 0）"
}
```

---

### rtt_stop

停止 RTT。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "RTT 已停止"
}
```

---

### rtt_read

读取 RTT 日志。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `buffer_index` | int | 否 | RTT 缓冲区索引，默认 0 |
| `size` | int | 否 | 读取大小（字节），默认 1024 |
| `timeout_ms` | int | 否 | 超时时间（毫秒） |

**返回值**:
```json
{
  "success": true,
  "data": "Hello, World!\n",
  "bytes_read": 14,
  "message": "成功读取 14 字节"
}
```

---

### rtt_write

向 RTT 写入数据。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `data` | string | 是 | 要写入的数据 |
| `buffer_index` | int | 否 | RTT 缓冲区索引，默认 0 |

**返回值**:
```json
{
  "success": true,
  "bytes_written": 13,
  "message": "成功写入 13 字节"
}
```

---

### rtt_get_status

获取 RTT 状态。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "started": true,
  "buffer_index": 0,
  "config": {"buffer_index": 0, "read_mode": "continuous", "timeout_ms": 1000},
  "message": "RTT 已启动"
}
```

---

## GDB Server (3个)

### start_gdb_server

启动 GDB Server。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `host` | string | 否 | 监听地址，默认 "0.0.0.0" |
| `port` | int | 否 | 监听端口，默认 2331 |
| `device` | string | 否 | 设备名称 |
| `interface` | string | 否 | 接口类型，默认 "JTAG" |
| `speed` | int | 否 | 接口速度（kHz），默认 4000 |

**返回值**:
```json
{
  "success": true,
  "message": "GDB Server 已启动，监听端口 2331"
}
```

---

### stop_gdb_server

停止 GDB Server。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "GDB Server 已停止"
}
```

---

### get_gdb_server_status

获取 GDB Server 状态。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "port": 2331,
    "connections": 0
  }
}
```

---

## SVD 工具 (5个)

### list_svd_devices

列出所有支持 SVD 的设备。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "devices": ["FC4150F1MBSxXxxxT1A", "FC7300F4MDDxXxxxT1C"],
  "count": 11
}
```

---

### get_svd_peripherals

获取指定设备的所有外设。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_name` | string | 是 | 设备名称 |

**返回值**:
```json
{
  "success": true,
  "device_name": "FC4150F1MBSxXxxxT1A",
  "peripherals": [{
    "name": "FLEXCAN0",
    "description": "FLEXCAN0",
    "base_address": "0x400A0000",
    "register_count": 59
  }],
  "count": 20
}
```

---

### get_svd_registers

获取指定外设的所有寄存器。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_name` | string | 是 | 设备名称 |
| `peripheral_name` | string | 是 | 外设名称 |

**返回值**:
```json
{
  "success": true,
  "device_name": "FC4150F1MBSxXxxxT1A",
  "peripheral_name": "FLEXCAN0",
  "base_address": "0x400A0000",
  "registers": [{
    "name": "MB0_CS",
    "address_offset": "0x80",
    "absolute_address": "0x400A0080",
    "size": 32,
    "access": "read-write"
  }],
  "count": 59
}
```

---

### read_register_with_fields

读取寄存器并解析字段。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_name` | string | 是 | 设备名称 |
| `peripheral_name` | string | 是 | 外设名称 |
| `register_name` | string | 是 | 寄存器名称 |

**返回值**:
```json
{
  "success": true,
  "device_name": "FC4150F1MBSxXxxxT1A",
  "peripheral_name": "FLEXCAN0",
  "register_name": "MB0_CS",
  "absolute_address": "0x400A0080",
  "raw_value": 0,
  "hex_value": "0x0",
  "fields": [{
    "field_name": "CODE",
    "field_value": 0,
    "bit_range": "[0:3]"
  }]
}
```

---

### parse_register_value

解析寄存器值（不读取硬件）。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `device_name` | string | 是 | 设备名称 |
| `peripheral_name` | string | 是 | 外设名称 |
| `register_name` | string | 是 | 寄存器名称 |
| `value` | int | 是 | 寄存器值 |

**返回值**:
```json
{
  "success": true,
  "raw_value": 255,
  "hex_value": "0xFF",
  "fields": [...]
}
```

---

## 使用指南与配置工具 (8个)

### get_usage_guidance

获取工具使用指南。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `category` | string | 否 | 工具分类关键字，如 connection/device_info/memory/flash/debug/rtt/svd/config |
| `include_examples` | bool | 否 | 是否包含示例，默认 true |

---

### get_best_practices

获取最佳实践。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `task_type` | string | 是 | 任务类型：read_registers/connect_device/memory_operations/flash_operations/debug |

---

### list_scenarios

列出所有可用场景。

**参数**: 无

---

### get_forbidden_operations

获取禁止操作列表。

**参数**: 无

---

### get_server_config

获取当前服务器运行时配置。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "default_interface": "JTAG",
    "svd_dir": "C:/svd_files",
    "patch_dir": "C:/patches",
    "generic_core_fallback": true,
    "default_core": "Cortex-M4",
    "resource_mode": "mixed",
    "env_overrides": {
      "JLINK_SVD_DIR": "C:/svd_files"
    }
  }
}
```

---

### get_server_capabilities

获取当前服务器能力状态。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "default_interface": "JTAG",
    "generic_core_fallback_enabled": true,
    "default_core": "Cortex-M4",
    "configured_resource_mode": "mixed",
    "current_connection_mode": "private",
    "current_connection_strategy": "patch_match:Flagchip",
    "connected_chip_name": "FC7300F4MDDxXxxxT1C",
    "private_patch_loaded": true,
    "svd_loaded": true,
    "gdb_server_binary_available": true,
    "semantic_enabled": true,
    "resource_mode": "mixed",
    "available_modes": ["native", "generic", "private"]
  }
}
```

---

### diagnose_environment

诊断环境和资源可用性。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "paths": {
      "svd_path": "C:/svd_files",
      "patch_manifest": "C:/patches/JLink_Patch_v2.45/JLinkDevices.xml",
      "gdb_server_binary": "C:/Program Files/SEGGER/JLink/JLinkGDBServerCL.exe"
    },
    "checks": {
      "generic_core_fallback_enabled": true,
      "svd_loaded": true,
      "patch_loaded": true,
      "gdb_server_binary_available": true
    },
    "warnings": [],
    "recommendations": []
  }
}
```

---

### get_system_prompt

获取系统提示词。

**参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `prompt_name` | string | 否 | 提示词名称，None 返回系统提示词 |

---

## 错误处理

所有工具失败时返回标准格式：

```json
{
  "success": false,
  "error": {
    "code": 101,
    "description": "连接失败",
    "suggestion": "请检查设备连接状态"
  }
}
```

### 错误代码详解

#### 通用错误 (1-99)

| 代码 | 描述 | 修复建议 |
|------|------|---------|
| 1 | 未知错误 | 检查日志或联系开发者 |
| 2 | JLink 未初始化 | 先调用 connect_device |
| 3 | JLink 已连接 | 先调用 disconnect_device |
| 4 | 参数无效 | 检查参数类型和值 |

#### 连接错误 (100-199)

| 代码 | 描述 | 修复建议 |
|------|------|---------|
| 100 | 未找到 JLink 设备 | 检查设备 USB 连接 |
| 101 | 连接失败 | 检查设备连接状态 |
| 102 | 连接断开 | 重新连接 |
| 103 | 目标芯片未连接 | 检查目标供电和连接线路 |

#### 操作错误 (200-299)

| 代码 | 描述 | 修复建议 |
|------|------|---------|
| 200 | 读取失败 | 检查地址有效性 |
| 201 | 写入失败 | 检查地址、数据和 Flash 锁定 |
| 202 | 擦除失败 | 检查 Flash 保护 |
| 203 | 校验失败 | 重新烧录 |
| 204 | 操作超时 | 复位后重试 |

#### 调试错误 (300-399)

| 代码 | 描述 | 修复建议 |
|------|------|---------|
| 300 | 目标正在运行 | 先调用 halt_cpu |
| 301 | 目标已暂停 | 无需操作 |
| 302 | 复位失败 | 检查连接和供电 |

#### RTT 错误 (400-499)

| 代码 | 描述 | 修复建议 |
|------|------|---------|
| 400 | RTT 未启动 | 调用 rtt_start |
| 401 | RTT 已启动 | 无需重复启动 |
| 402 | RTT 缓冲区未找到 | 确保固件启用 RTT |

#### GDB Server 错误 (500-599)

| 代码 | 描述 | 修复建议 |
|------|------|---------|
| 500 | GDB Server 启动失败 | 检查端口占用 |
| 501 | GDB Server 未运行 | 调用 start_gdb_server |
| 502 | GDB Server 已运行 | 先调用 stop_gdb_server |


