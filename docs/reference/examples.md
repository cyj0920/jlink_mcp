# JLink MCP 使用示例

## 基础使用流程

### 1. 列出可用设备

```
list_jlink_devices()
```

返回：
```json
[{
  "serial_number": "941000024",
  "product_name": "J-Link",
  "connection_type": "USB"
}]
```

---

### 2. 连接到设备

**自动连接**（推荐用于未知芯片）：
```
connect_device()
```

**指定 Flagchip 芯片**：
```
connect_device(chip_name="FC4150F2MBSxXxxxT1A")
```

**指定设备序列号**：
```
connect_device(serial_number="941000024")
```

---

### 3. 查看设备信息

**获取芯片信息**：
```
get_target_info()
```

返回：
```json
{
  "success": true,
  "data": {
    "device_name": "FC4150F2MBSxXxxxT1A",
    "core_type": "Cortex-M4",
    "flash_size": 2097152,
    "ram_size": 196608
  }
}
```

**查看电压**：
```
get_target_voltage()
```

---

## 内存操作示例

### 读取内存

**读取 16 字节**：
```
read_memory(address="0x20000000", size=16)
```

返回：
```json
{
  "success": true,
  "data": {
    "address": "0x20000000",
    "data": [0x12, 0x34, 0x56, 0x78, 0x00, 0x00, 0x00, 0x00,
            0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00],
    "hex_string": "78563412000000000000000000000000"
  }
}
```

**读取 8 位数据**：
```
read_memory(address="0x20000000", size=4, width=8)
```

---

### 写入内存

**写入 32 位数据**：
```
write_memory(address="0x20000000", data="0x12345678")
```

**写入 16 位数据**：
```
write_memory(address="0x20000000", data="0x1234", width=16)
```

---

### 读写寄存器

**读取所有寄存器**：
```
read_registers()
```

**读取指定寄存器**：
```
read_registers(registers=["R0", "PC", "SP"])
```

**写入寄存器**：
```
write_register(register="R0", value=0x12345678)
```

**设置程序计数器**：
```
write_register(register="PC", value=0x08000100)
```

---

## Flash 操作示例

### 烧录固件

**烧录二进制文件**：
```
program_flash(file_path="C:/firmware/app.bin")
```

**烧录 HEX 文件（指定地址）**：
```
program_flash(file_path="C:/firmware/app.hex", address=0x08000000)
```

**烧录 ELF 文件**：
```
program_flash(file_path="C:/firmware/app.elf")
```

---

### 验证固件

```
verify_flash(file_path="C:/firmware/app.bin")
```

返回：
```json
{
  "success": true,
  "data": {
    "verified": true,
    "bytes_verified": 65536
  }
}
```

---

### 擦除 Flash

**擦除整片**：
```
erase_flash()
```

**擦除指定区域**：
```
erase_flash(address=0x08000000, size=65536)
```

---

## 调试控制示例

### 复位目标

**正常复位**：
```
reset_target()
```

**复位后暂停**（用于立即调试）：
```
reset_target(type="halt")
```

**仅复位核心**：
```
reset_target(type="core")
```

---

### 控制执行

**暂停 CPU**：
```
halt_cpu()
```

**运行 CPU**：
```
run_cpu()
```

**单步执行**：
```
step_instruction()
```

**查看 CPU 状态**：
```
get_cpu_state()
```

---

### 断点操作

**设置断点**：
```
set_breakpoint(address="0x08000100")
```

**清除断点**：
```
clear_breakpoint(address="0x08000100")
```

**调试流程示例**：
```
# 1. 连接设备
connect_device(chip_name="FC4150F2MBSxXxxxT1A")

# 2. 复位并暂停
reset_target(type="halt")

# 3. 设置断点
set_breakpoint(address="0x08000100")

# 4. 运行
run_cpu()

# 5. 检查状态
get_cpu_state()

# 6. 单步执行
step_instruction()

# 7. 读取寄存器
read_registers()
```

---

## RTT 使用示例

### 启动 RTT

```
rtt_start()
```

---

### 读取日志

**读取日志（默认 1KB）**：
```
rtt_read()
```

**读取大量日志（4KB）**：
```
rtt_read(max_bytes=4096)
```

返回：
```json
{
  "success": true,
  "data": {
    "bytes_read": 256,
    "text": "Hello, World!\nSystem started...\n",
    "hex_data": "48656C6C6F2C20576F726C64210A53797374656D20737461727465642E2E2E0A"
  }
}
```

---

### 写入数据

**发送字符串**：
```
rtt_write(data="Hello, RTT!")
```

**发送十六进制数据**：
```
rtt_write(data="0x48656C6C6F")
```

---

### 查看状态

```
rtt_get_status()
```

---

### 停止 RTT

```
rtt_stop()
```

---

## GDB Server 使用示例

### 启动 GDB Server

```
start_gdb_server()
```

**指定端口**：
```
start_gdb_server(port=2331)
```

---

### 查看状态

```
get_gdb_server_status()
```

返回：
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

### 停止 GDB Server

```
stop_gdb_server()
```

---

### 与 GDB 配合使用

在 GDB 中连接：
```
(gdb) target remote localhost:2331
(gdb) monitor reset
(gdb) load firmware.elf
(gdb) continue
```

---

## Flagchip 专用示例

### 设备名称智能匹配

**简化名称自动匹配**：
```
# 使用简化名称，系统自动匹配到完整名称
connect_device(chip_name="FC7300F4MDD")
# 自动匹配到: FC7300F4MDDxXxxxT1C (T1C 批次)

connect_device(chip_name="FC7300F4MDS")
# 自动匹配到: FC7300F4MDSxXxxxT1C (T1C 批次)

connect_device(chip_name="FC4150F1M")
# 自动匹配到: FC4150F1MBSxXxxxT1B (T1B 批次，无 T1C)
```

**批次版本优先级**：
- T1C > T1B > T1A
- 自动选择最新批次
- 排除 Unlock/Factory/FromRom 特殊版本

**匹配失败提示**：
```
connect_device(chip_name="UNKNOWN_CHIP")
# 返回相似设备建议
```

---

### FC7300 实际测试示例（已验证）

**测试环境**:
- 芯片: FC7300F4MDSXXXXXT1C
- 连接: J-Link V11 via JTAG
- 日期: 2026-02-10

**完整测试流程**:
```
# 1. 查看支持的 Flagchip 设备
list_flagchip_devices()

# 2. 使用简化名称连接（默认 JTAG）
connect_device(chip_name="FC7300F4MDD")
# 自动匹配到: FC7300F4MDDxXxxxT1C

# 3. 获取设备信息
get_target_info()
# 返回: Cortex-M7 r1p2, Big endian

# 4. 复位设备（已验证通过）
reset_target(reset_type="normal")

# 5. 读取寄存器（已验证通过）
read_registers(register_names=["R0", "R15 (PC)", "R13 (SP)"])
# 示例返回值:
#   R0 = 0x0
#   R15 (PC) = -0x2
#   R13 (SP) = -0x4

# 6. 断开连接（已验证通过）
disconnect_device()
```

---

### 列出支持的 Flagchip 设备

```
list_flagchip_devices()
```

返回：
```json
{
  "success": true,
  "device_count": 57,
  "device_names": [
    "FC4150F2MBSxXxxxT1A",
    "FC4150F1MBSxXxxxT1A",
    "FC7300F8MDQxXxxxT1B",
    "FC7300F4MDSxXxxxT1C",
    ...
  ]
}
```

---

### 连接到 Flagchip 设备

**推荐方式**（默认 JTAG，支持智能匹配）：
```
# 方式 1: 使用简化名称，自动匹配
connect_device(chip_name="FC7300F4MDD")
# 自动匹配到: FC7300F4MDDxXxxxT1C

# 方式 2: 完整名称
connect_device(chip_name="FC7300F4MDSxXxxxT1C")

# 方式 3: 不指定芯片名称，自动检测
connect_device()
# 默认使用 JTAG 接口
```

**指定接口**（如果需要）：
```
# 使用 SWD 接口（如果硬件支持）
connect_device(chip_name="FC7300F4MDD", interface="SWD")

# 使用 JTAG 接口（推荐，默认）
connect_device(chip_name="FC7300F4MDD", interface="JTAG")
```

---

## 完整工作流程示例

### 示例 1: 烧录固件并验证

```
# 1. 列出设备
list_jlink_devices()

# 2. 连接到设备
connect_device(chip_name="FC4150F2MBSxXxxxT1A")

# 3. 查看设备信息
get_target_info()

# 4. 复位设备
reset_target()

# 5. 擦除 Flash
erase_flash()

# 6. 烧录固件
program_flash(file_path="C:/firmware/app.bin")

# 7. 验证固件
verify_flash(file_path="C:/firmware/app.bin")

# 8. 断开连接
disconnect_device()
```

---

### 示例 2: 调试应用程序

```
# 1. 连接设备
connect_device(chip_name="FC4150F2MBSxXxxxT1A")

# 2. 复位并暂停
reset_target(type="halt")

# 3. 设置断点
set_breakpoint(address="0x08000100")

# 4. 运行到断点
run_cpu()

# 5. 检查状态
get_cpu_state()

# 6. 读取寄存器
read_registers()

# 7. 读取内存
read_memory(address="0x20000000", size=16)

# 8. 单步执行
step_instruction()

# 9. 清除断点
clear_breakpoint(address="0x08000100")

# 10. 继续运行
run_cpu()
```

---

### 示例 3: 使用 RTT 查看日志

```
# 1. 连接设备
connect_device(chip_name="FC4150F2MBSxXxxxT1A")

# 2. 复位设备
reset_target()

# 3. 启动 RTT
rtt_start()

# 4. 运行程序
run_cpu()

# 5. 读取日志
rtt_read()

# 6. 发送命令
rtt_write(data="status\n")

# 7. 读取响应
rtt_read()

# 8. 停止 RTT
rtt_stop()
```

---

### 示例 4: 使用 GDB Server

```
# 1. 连接设备
connect_device(chip_name="FC4150F2MBSxXxxxT1A")

# 2. 启动 GDB Server
start_gdb_server(port=2331)

# 3. 在 GDB 中连接
# gdb-multiarch
# (gdb) target remote localhost:2331
# (gdb) monitor reset halt
# (gdb) load firmware.elf
# (gdb) b main
# (gdb) continue

# 4. 停止 GDB Server
stop_gdb_server()
```

---

## 错误处理示例

### 设备未连接

```
read_memory(address="0x20000000", size=16)
```

返回：
```json
{
  "success": false,
  "error": {
    "code": 100,
    "description": "设备未连接",
    "suggestion": "请先调用 connect_device()"
  }
}
```

---

### 芯片有读保护

```
connect_device()
```

返回：
```json
{
  "success": false,
  "error": {
    "code": 103,
    "description": "读保护检测",
    "suggestion": "请使用解锁脚本解除芯片读保护"
  }
}
```

---

## 提示

1. **地址格式**：支持十进制或十六进制字符串（如 "0x20000000"）
2. **数据格式**：写入数据使用十六进制字符串（如 "0x12345678"）
3. **连接后断开**：使用完毕后记得调用 `disconnect_device()`
4. **Flash 操作**：擦除和烧录可能需要较长时间
5. **RTT 使用**：需要目标芯片实现 RTT 功能