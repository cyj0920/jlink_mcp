# JLink MCP 硬件测试指南

本指南介绍如何验证 JLink MCP 服务器功能。

## 测试检查清单

### 环境准备

- [ ] Python 3.10+ 已安装
- [ ] 项目依赖已安装 (`pip install -e .`)
- [ ] pytest 已安装
- [ ] JLink 驱动已安装
- [ ] JLink 调试器已连接 USB

### 硬件准备

- [ ] JLink 调试器已连接电脑
- [ ] 目标芯片已供电
- [ ] 调试接口已连接 (JTAG/SWD)

---

## 测试脚本

### tests/integration/test_fc7300.py - FC7300 集成测试

```bash
pytest tests/integration/test_fc7300.py -v -m integration
```

### tests/integration/test_device_matching.py - 设备匹配测试

```bash
pytest tests/integration/test_device_matching.py -v
```

### tests/mock/ - Mock 测试

```bash
pytest tests/mock/ -v
```

### tests/unit/ - 单元测试

```bash
pytest tests/unit/ -v
```

---

## 运行所有测试

```bash
# 运行所有测试
pytest tests/ -v

# 仅运行不需要硬件的测试
pytest tests/unit tests/mock -v

# 运行集成测试（需要硬件）
pytest tests/integration/ -v -m integration
```

---

## 已验证的功能

### FC7300F4MDSXXXXXT1C (Flagchip)
- 设备连接
- 复位控制
- 寄存器读取
- 断开连接
- SVD 文件加载（11 个设备）
- 外设查询（FLEXCAN0: 59 个寄存器）
- 寄存器字段解析

---

## 测试场景

### 场景 1：基本连接测试

```python
# 测试步骤
1. list_jlink_devices()     # 期望: 返回设备列表
2. connect_device(chip_name="FC7300F4MDD")  # 期望: success=true
3. get_target_info()        # 期望: 返回芯片信息
4. disconnect_device()      # 期望: success=true
```

### 场景 2：内存读写测试

```python
# 测试步骤
1. connect_device(chip_name="FC7300F4MDD")
2. halt_cpu()
3. write_memory(address=0x20000000, data=b'\x11\x22\x33\x44')
4. read_memory(address=0x20000000, size=4)
5. # 期望: 返回 [0x11, 0x22, 0x33, 0x44]
6. run_cpu()
7. disconnect_device()
```

### 场景 3：Flash 操作测试

```python
# 测试步骤
1. connect_device(chip_name="FC7300F4MDD")
2. erase_flash(chip_erase=True)  # 期望: success=true
3. program_flash(address=0x08000000, data=test_data, verify=True)
4. verify_flash(address=0x08000000, data=test_data)
5. reset_target()
6. disconnect_device()
```

### 场景 4：调试控制测试

```python
# 测试步骤
1. connect_device(chip_name="FC7300F4MDD")
2. reset_target(reset_type="halt")
3. get_cpu_state()          # 期望: halted=true
4. set_breakpoint(address=0x08000100)
5. run_cpu()
6. # 等待断点命中
7. get_cpu_state()          # 期望: pc=0x08000100
8. clear_breakpoint(address=0x08000100)
9. disconnect_device()
```

### 场景 5：SVD 解析测试

```python
# 测试步骤
1. list_svd_devices()       # 期望: 返回设备列表
2. get_svd_peripherals(device_name="FC4150F1MBSxXxxxT1A")
3. get_svd_registers(device_name="...", peripheral_name="FLEXCAN0")
4. read_register_with_fields(...)  # 需要设备连接
```

---

## 预期结果示例

### 成功连接输出

```json
{
  "success": true,
  "serial_number": "941000024",
  "message": "成功连接到设备 941000024，接口: JTAG"
}
```

### 设备信息输出

```json
{
  "success": true,
  "data": {
    "device_name": "FC7300F4MDDxXxxxT1C",
    "core_type": "Cortex-M4",
    "flash_size": 262144,
    "ram_size": 32768
  }
}
```

### 错误输出示例

```json
{
  "success": false,
  "error": {
    "code": 100,
    "description": "未找到 JLink 设备",
    "suggestion": "检查 USB 连接或重新插拔设备"
  }
}
```

---

## 故障排除

### JLink 设备占用

1. 关闭其他 JLink 应用
2. 拔掉 JLink USB 连接线，等待 5 秒后重新插入
3. 结束 `JLink.exe` 进程

### 导入错误

```bash
pip install -e .
```

### 设备未找到

- 检查 USB 连接
- 检查 JLink 驱动
- 尝试不同的 USB 端口

---

## 测试报告模板

测试完成后，建议记录以下信息：

```
## 测试报告

**日期**: 2024-01-15
**测试人员**: 张三
**JLink 型号**: J-Link V11
**固件版本**: V2.45
**目标芯片**: FC7300F4MDSXXXXXT1C

### 测试结果

| 测试项 | 结果 | 备注 |
|--------|------|------|
| 设备枚举 | ✓ PASS | - |
| 设备连接 | ✓ PASS | JTAG 模式 |
| 电压检测 | ✓ PASS | 3.3V |
| 芯片识别 | ✓ PASS | - |
| 内存读取 | ✓ PASS | - |
| Flash 烧录 | ✓ PASS | 64KB |
| 复位控制 | ✓ PASS | - |

### 问题记录

无

### 环境信息

- Python: 3.12.9
- OS: Windows 11
- jlink-mcp: v0.1.1
```

---

## 报告问题

如果测试失败，请提供：
1. 错误信息
2. JLink 型号和固件版本
3. 目标芯片型号
4. 测试脚本输出
