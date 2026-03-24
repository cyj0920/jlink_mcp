# JLink MCP 使用示例

## 基础流程

### 1. 列出设备

```
list_jlink_devices()
```

### 2. 连接设备

```
# 自动匹配芯片名称
connect_device(chip_name="FC7300F4MDD")

# 指定接口
connect_device(chip_name="FC7300F4MDD", interface="JTAG")
```

### 3. 查看设备信息

```
get_target_info()
get_target_voltage()
```

---

## 内存操作

### 读取内存

```
read_memory(address=0x20000000, size=16)
read_memory(address=0x20000000, size=4, width=8)
```

### 写入内存

```
write_memory(address=0x20000000, data=b'\x78\x56\x34\x12')
```

### 读写寄存器

```
# 读取所有寄存器
read_registers()

# 读取指定寄存器
read_registers(register_names=["R0", "R15 (PC)", "R13 (SP)"])

# 写入寄存器
write_register(register_name="R0", value=0x12345678)
```

---

## Flash 操作

### 烧录固件

```
# 擦除整片
erase_flash(chip_erase=True)

# 烧录（需要先读取文件）
program_flash(address=0x08000000, data=firmware_data, verify=True)
```

### 验证固件

```
verify_flash(address=0x08000000, data=expected_data)
```

---

## 调试控制

### CPU 控制

```
# 复位
reset_target()           # 正常复位
reset_target(reset_type="halt")  # 复位后暂停

# 暂停/运行
halt_cpu()
run_cpu()

# 单步
step_instruction()

# 状态
get_cpu_state()
```

### 断点

```
set_breakpoint(address=0x08000100)
clear_breakpoint(address=0x08000100)
```

---

## RTT 使用

```
# 启动
rtt_start()

# 读取日志
rtt_read()

# 写入数据
rtt_write(data="command")

# 状态
rtt_get_status()

# 停止
rtt_stop()
```

---

## GDB Server

```
# 启动
start_gdb_server(port=2331)

# 状态
get_gdb_server_status()

# 停止
stop_gdb_server()
```

在 GDB 中连接：
```
(gdb) target remote localhost:2331
```

---

## SVD 寄存器解析

```
# 列出设备
list_svd_devices()

# 获取外设
get_svd_peripherals(device_name="FC4150F1MBSxXxxxT1A")

# 获取寄存器
get_svd_registers(device_name="FC4150F1MBSxXxxxT1A", peripheral_name="FLEXCAN0")

# 读取并解析
read_register_with_fields(
    device_name="FC4150F1MBSxXxxxT1A",
    peripheral_name="FLEXCAN0",
    register_name="MB0_CS"
)

# 仅解析
parse_register_value(
    device_name="FC4150F1MBSxXxxxT1A",
    peripheral_name="FLEXCAN0",
    register_name="MB0_CS",
    value=0xFF
)
```

---

## Flagchip 专用

### 芯片名称匹配

```
match_chip_name(chip_name="FC7300F4MDD")
# 返回: FC7300F4MDDxXxxxT1C
```

### 智能匹配规则

- 前缀匹配：FC7300F4MDD → FC7300F4MDDxXxxxT1C
- 批次优先级：T1C > T1B > T1A
- 排除特殊版本：Unlock/Factory/FromRom

---

## 完整工作流示例

### 固件烧录

```
# 1. 连接
connect_device(chip_name="FC7300F4MDD")

# 2. 查看信息
get_target_info()

# 3. 擦除
erase_flash(chip_erase=True)

# 4. 烧录
program_flash(address=0x08000000, data=firmware_data, verify=True)

# 5. 复位运行
reset_target()

# 6. 断开
disconnect_device()
```

### 调试应用程序

```
# 1. 连接
connect_device(chip_name="FC7300F4MDD")

# 2. 复位暂停
reset_target(reset_type="halt")

# 3. 设置断点
set_breakpoint(address=0x08000100)

# 4. 运行
run_cpu()

# 5. 检查状态
get_cpu_state()

# 6. 读取寄存器
read_registers()

# 7. 单步
step_instruction()

# 8. 清除断点
clear_breakpoint(address=0x08000100)

# 9. 继续运行
run_cpu()
```

### RTT 日志查看

```
# 1. 连接
connect_device(chip_name="FC7300F4MDD")

# 2. 复位
reset_target()

# 3. 启动 RTT
rtt_start()

# 4. 运行
run_cpu()

# 5. 读取日志
rtt_read()

# 6. 停止 RTT
rtt_stop()
```

---

## 使用指南工具

```
# 获取指南
get_usage_guidance()
get_usage_guidance(category="connection")

# 最佳实践
get_best_practices(task_type="connect_device")

# 场景列表
list_scenarios()

# 禁止操作
get_forbidden_operations()

# 系统提示词
get_system_prompt()
```

---

## 高级场景

### 固件升级工作流

```
# 完整的固件升级流程
connect_device(chip_name="FC7300F4MDD")

# 1. 检查设备信息
info = get_target_info()
print(f"芯片: {info['data']['device_name']}")
print(f"Flash: {info['data']['flash_size']} bytes")

# 2. 检查当前固件版本（假设存储在地址 0x08000000）
version_data = read_memory(address=0x08000000, size=4)
print(f"当前版本: {version_data['data']}")

# 3. 擦除 Flash
erase_flash(chip_erase=True)

# 4. 烧录新固件
with open("firmware_v2.bin", "rb") as f:
    firmware = f.read()
program_flash(address=0x08000000, data=firmware, verify=True)

# 5. 验证并运行
verify_flash(address=0x08000000, data=firmware)
reset_target()

disconnect_device()
```

### 生产测试流程

```
# 批量生产测试
def test_chip(chip_name):
    # 连接
    result = connect_device(chip_name=chip_name)
    if not result['success']:
        return "FAIL: 连接失败"

    # 检查电压
    voltage = get_target_voltage()
    if voltage['data']['voltage_v'] < 3.0:
        return "FAIL: 电压过低"

    # 检查 Flash
    info = get_target_info()
    if info['data']['flash_size'] < 262144:
        return "FAIL: Flash 容量不足"

    # 烧录测试固件
    erase_flash(chip_erase=True)
    program_flash(address=0x08000000, data=test_firmware, verify=True)

    # 运行自检
    reset_target()
    rtt_start()
    logs = rtt_read()
    rtt_stop()

    disconnect_device()

    if "PASS" in logs['data']:
        return "PASS"
    return "FAIL: 自检未通过"

# 批量测试
chips = ["FC7300F4MDD", "FC7300F4MDS"]
for chip in chips:
    result = test_chip(chip)
    print(f"{chip}: {result}")
```

### 多芯片测试

```
# 测试多个芯片
chips = ["FC7300F4MDD", "FC7300F4MDS", "FC4150F1MBS"]

for chip in chips:
    connect_device(chip_name=chip)
    info = get_target_info()
    print(f"{chip}: Flash={info['data']['flash_size']}B")
    disconnect_device()
```

### 寄存器监控

```
# 持续监控寄存器变化
connect_device(chip_name="FC7300F4MDD")
halt_cpu()

for i in range(10):
    regs = read_registers(register_names=["R0", "PC"])
    print(f"R0={regs['registers'][0]['value']:#x}")
    step_instruction()

run_cpu()
disconnect_device()
```

### Flash 批量烧录

```
# 读取固件文件
with open("firmware.bin", "rb") as f:
    firmware = f.read()

connect_device(chip_name="FC7300F4MDD")
erase_flash(chip_erase=True)
program_flash(address=0x08000000, data=firmware, verify=True)
reset_target()
disconnect_device()
```

---

## 错误处理最佳实践

### 检查返回值

```
# 始终检查 success 字段
result = connect_device(chip_name="FC7300F4MDD")
if not result['success']:
    error = result['error']
    print(f"错误 [{error['code']}]: {error['description']}")
    print(f"建议: {error['suggestion']}")
    return
```

### 安全操作模式

```
# 使用 try-finally 确保资源释放
connect_device(chip_name="FC7300F4MDD")
try:
    halt_cpu()
    # 执行操作...
    data = read_memory(address=0x20000000, size=16)
finally:
    run_cpu()
    disconnect_device()
```

### 重试机制

```
# 带重试的操作
def safe_read(address, size, max_retries=3):
    for attempt in range(max_retries):
        result = read_memory(address=address, size=size)
        if result['success']:
            return result

        if attempt < max_retries - 1:
            print(f"重试 {attempt + 1}/{max_retries}...")
            reset_target()

    return result
```

### 状态验证

```
# 操作前验证状态
def safe_halt():
    state = get_cpu_state()
    if state['halted']:
        return  # 已经暂停

    if not state['running']:
        reset_target(reset_type="halt")

    halt_cpu()
```

---

## 调试技巧

### 1. 检查连接状态

```
status = get_connection_status()
if not status['data']['connected']:
    print("设备未连接")
```

### 2. 验证芯片名称

```
result = match_chip_name("FC7300F4MDD")
if result['success']:
    print(f"匹配到: {result['matched']}")
```

### 3. 安全读取内存

```
try:
    halt_cpu()
    data = read_memory(address=0x20000000, size=16)
except Exception as e:
    print(f"读取失败: {e}")
finally:
    run_cpu()
```

---

---

## 提示

1. **地址格式**：支持十进制或十六进制整数 (0x20000000)
2. **数据格式**：写入数据使用 bytes 类型
3. **芯片名称**：支持简化名称自动匹配
4. **默认接口**：JTAG
5. **使用完毕**：记得调用 disconnect_device()
