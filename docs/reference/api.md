# JLink MCP API 文档

## 概述

JLink MCP 服务器提供 30 个工具，用于与 JLink 调试器和目标芯片进行交互。所有工具都可以通过 iFlow CLI 调用。

---

## 连接管理 (4个工具)

### 1. list_jlink_devices

列出所有连接的 JLink 设备。

**参数**: 无

**返回值**:
```json
{
  "serial_number": "设备序列号",
  "product_name": "产品名称",
  "firmware_version": "固件版本",
  "connection_type": "连接类型 (USB/ETH)"
}
```

**示例**:
```
list_jlink_devices()
```

---

### 2. connect_device

连接到 JLink 设备。

**参数**:
- `serial_number` (可选): 设备序列号，None 则连接第一个设备
- `interface` (可选): 目标接口类型，默认 "JTAG"，可选 "SWD"
- `chip_name` (可选): 芯片名称，支持简化名称（如 FC7300F4MDD），会自动匹配到完整名称

**返回值**:
```json
{
  "success": true,
  "serial_number": "设备序列号",
  "message": "成功连接到设备"
}
```

**示例**:
```
connect_device()  # 自动连接
connect_device(serial_number="941000024")  # 指定设备
connect_device(chip_name="FC4150F2MBSxXxxxT1A")  # 指定芯片

# FC7300 实际验证（2026-02-10）
connect_device(interface="JTAG")  # 使用 JTAG 接口
```

**硬件验证状态**:
- ✅ FC7300F4MDSXXXXXT1C - JTAG 连接测试通过
- 自动检测会尝试所有 Flagchip 设备（57个）
- 如果自动检测失败，会回退到常见芯片配置

---

### 3. disconnect_device

断开 JLink 设备连接。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "设备已断开连接"
}
```

**示例**:
```
disconnect_device()
```

---

### 4. get_connection_status

获取当前连接状态。

**参数**: 无

**返回值**:
```json
{
  "connected": true,
  "device_serial": "设备序列号",
  "target_interface": "JTAG",
  "target_voltage": 3.3,
  "target_connected": true,
  "firmware_version": "V2.45"
}
```

**示例**:
```
get_connection_status()
```

---

## 设备信息 (4个工具)

### 5. get_target_info

获取目标设备（MCU）信息。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "device_name": "FC4150F2MBSxXxxxT1A",
    "core_type": "Cortex-M4",
    "core_id": 0x6BA02477,
    "device_id": 0x00000000,
    "flash_size": 2097152,
    "ram_size": 196608,
    "ram_addresses": ["0x20000000"]
  }
}
```

**示例**:
```
get_target_info()
```

---

### 6. get_target_voltage

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

**示例**:
```
get_target_voltage()
```

---

### 7. scan_target_devices

扫描目标总线上的设备。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "device_count": 1,
  "devices": [0x6BA02477]
}
```

**示例**:
```
scan_target_devices()
```

---

### 8. list_flagchip_devices

列出 Flagchip 补丁支持的设备。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "device_count": 57,
  "devices": [
    {
      "name": "FC4150F2MBSxXxxxT1A",
      "vendor": "Flagchip",
      "core": "JLINK_CORE_CORTEX_M4",
      "work_ram_addr": "0x20000000",
      "work_ram_size": "0x30000"
    }
  ],
  "device_names": ["FC4150F2MBSxXxxxT1A", "FC4150F1MBSxXxxxT1A", ...]
}
```

**示例**:
```
list_flagchip_devices()
```

**智能匹配说明**:
- 支持简化的芯片名称自动匹配：`FC7300F4MDD` → `FC7300F4MDDxXxxxT1C`
- 批次版本优先级：T1C > T1B > T1A，自动选择最新批次
- 多匹配时会排除 Unlock/Factory/FromRom 特殊版本

---

## 内存操作 (4个工具)

### 9. read_memory

读取指定地址的内存。

**参数**:
- `address`: 内存地址（十进制或十六进制字符串，如 "0x20000000"）
- `size`: 读取大小（字节）
- `width` (可选): 数据宽度，默认 32，可选 8/16/32

**返回值**:
```json
{
  "success": true,
  "data": {
    "address": "0x20000000",
    "data": [0x12, 0x34, 0x56, 0x78],
    "hex_string": "78563412"
  }
}
```

**示例**:
```
read_memory(address="0x20000000", size=16)
read_memory(address=536870912, size=16, width=8)
```

---

### 10. write_memory

写入内存。

**参数**:
- `address`: 内存地址
- `data`: 数据（十六进制字符串，如 "0x12345678"）
- `width` (可选): 数据宽度，默认 32

**返回值**:
```json
{
  "success": true,
  "message": "成功写入 4 字节到 0x20000000"
}
```

**示例**:
```
write_memory(address="0x20000000", data="0x12345678")
write_memory(address="0x20000000", data="0x1234", width=16)
```

---

### 11. read_registers

读取 CPU 寄存器。

**参数**:
- `registers` (可选): 要读取的寄存器列表，默认读取所有通用寄存器

**返回值**:
```json
{
  "success": true,
  "data": {
    "R0": 0x00000000,
    "R1": 0x00000001,
    "R2": 0x00000002,
    "PC": 0x08000100,
    "SP": 0x20010000
  }
}
```

**示例**:
```
read_registers()  # 读取所有寄存器
read_registers(registers=["R0", "PC", "SP"])  # 读取指定寄存器
```

---

### 12. write_register

写入单个寄存器。

**参数**:
- `register`: 寄存器名称（如 "R0", "PC", "SP"）
- `value`: 寄存器值

**返回值**:
```json
{
  "success": true,
  "message": "成功写入寄存器 R0 = 0x12345678"
}
```

**示例**:
```
write_register(register="R0", value=0x12345678)
write_register(register="PC", value=0x08000100)
```

---

## Flash 操作 (3个工具)

### 13. erase_flash

擦除 Flash。

**参数**:
- `address` (可选): 起始地址，默认 0
- `size` (可选): 擦除大小（字节），默认擦除整片

**返回值**:
```json
{
  "success": true,
  "message": "成功擦除 2097152 字节 Flash"
}
```

**示例**:
```
erase_flash()  # 擦除整片
erase_flash(address=0, size=65536)  # 擦除指定区域
```

---

### 14. program_flash

烧录固件到 Flash。

**参数**:
- `file_path`: 固件文件路径（.hex, .bin, .elf）
- `address` (可选): 起始地址，默认 0

**返回值**:
```json
{
  "success": true,
  "message": "成功烧录 65536 字节到 0x08000000"
}
```

**示例**:
```
program_flash(file_path="C:/firmware/app.bin")
program_flash(file_path="C:/firmware/app.hex", address=0x08000000)
```

---

### 15. verify_flash

校验 Flash 内容。

**参数**:
- `file_path`: 固件文件路径
- `address` (可选): 起始地址，默认 0

**返回值**:
```json
{
  "success": true,
  "data": {
    "verified": true,
    "bytes_verified": 65536
  }
}
```

**示例**:
```
verify_flash(file_path="C:/firmware/app.bin")
```

---

## 调试控制 (7个工具)

### 16. reset_target

复位目标芯片。

**参数**:
- `type` (可选): 复位类型，默认 "normal"，可选 "halt", "core"

**返回值**:
```json
{
  "success": true,
  "message": "成功复位目标芯片"
}
```

**示例**:
```
reset_target()  # 正常复位
reset_target(type="halt")  # 复位后暂停
```

---

### 17. halt_cpu

暂停 CPU 执行。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "CPU 已暂停"
}
```

**示例**:
```
halt_cpu()
```

---

### 18. run_cpu

运行 CPU。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "CPU 已开始运行"
}
```

**示例**:
```
run_cpu()
```

---

### 19. step_instruction

单步执行一条指令。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "pc": 0x08000100,
    "instruction": "0x47F0"
  }
}
```

**示例**:
```
step_instruction()
```

---

### 20. get_cpu_state

获取 CPU 运行状态。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "is_halted": true,
    "halt_reason": "breakpoint",
    "pc": 0x08000100
  }
}
```

**示例**:
```
get_cpu_state()
```

---

### 21. set_breakpoint

设置断点。

**参数**:
- `address`: 断点地址

**返回值**:
```json
{
  "success": true,
  "message": "成功在 0x08000100 设置断点"
}
```

**示例**:
```
set_breakpoint(address="0x08000100")
```

---

### 22. clear_breakpoint

清除断点。

**参数**:
- `address`: 断点地址

**返回值**:
```json
{
  "success": true,
  "message": "成功清除 0x08000100 的断点"
}
```

**示例**:
```
clear_breakpoint(address="0x08000100")
```

---

## RTT 工具 (5个工具)

### 23. rtt_start

启动 RTT（实时传输）。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "RTT 已启动"
}
```

**示例**:
```
rtt_start()
```

---

### 24. rtt_stop

停止 RTT。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "RTT 已停止"
}
```

**示例**:
```
rtt_stop()
```

---

### 25. rtt_read

读取 RTT 日志。

**参数**:
- `max_bytes` (可选): 最大读取字节数，默认 1024

**返回值**:
```json
{
  "success": true,
  "data": {
    "bytes_read": 256,
    "text": "Hello, World!\n",
    "hex_data": "48656C6C6F2C20576F726C64210A"
  }
}
```

**示例**:
```
rtt_read()
rtt_read(max_bytes=4096)
```

---

### 26. rtt_write

向 RTT 写入数据。

**参数**:
- `data`: 要写入的数据（字符串或十六进制）

**返回值**:
```json
{
  "success": true,
  "message": "成功写入 13 字节"
}
```

**示例**:
```
rtt_write(data="Hello, RTT!")
rtt_write(data="0x48656C6C6F")
```

---

### 27. rtt_get_status

获取 RTT 状态。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "data": {
    "is_running": true,
    "channel_count": 1,
    "buffer_size": 1024
  }
}
```

**示例**:
```
rtt_get_status()
```

---

## GDB Server (3个工具)

### 28. start_gdb_server

启动 GDB Server。

**参数**:
- `port` (可选): GDB Server 端口，默认 2331

**返回值**:
```json
{
  "success": true,
  "message": "GDB Server 已启动，监听端口 2331"
}
```

**示例**:
```
start_gdb_server()
start_gdb_server(port=2331)
```

---

### 29. stop_gdb_server

停止 GDB Server。

**参数**: 无

**返回值**:
```json
{
  "success": true,
  "message": "GDB Server 已停止"
}
```

**示例**:
```
stop_gdb_server()
```

---

### 30. get_gdb_server_status

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

**示例**:
```
get_gdb_server_status()
```

---

## 错误处理

所有工具在失败时都会返回标准错误格式：

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

## 常见错误代码

| 错误代码 | 描述 | 修复建议 |
|---------|------|---------|
| 100 | 设备未连接 | 请先调用 connect_device() |
| 101 | 连接失败 | 检查设备连接和芯片名称 |
| 102 | 目标未连接 | 检查目标芯片供电 |
| 103 | 读保护检测 | 解除芯片读保护 |
| 200 | 内存访问失败 | 检查地址范围 |
| 300 | Flash 操作失败 | 检查 Flash 是否被锁定 |