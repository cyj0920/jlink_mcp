# JLink MCP 常见问题解答 (FAQ)

## 硬件测试验证

### 已验证的芯片

**✅ FC7300F4MDSXXXXXT1C** (Flagchip)
- 测试日期: 2026-02-10
- 连接方式: JTAG
- 测试设备: J-Link V11 (S/N: 941000024)

**测试通过的功能**:
- ✅ 设备连接和枚举
- ✅ 自动芯片检测（使用 STM32F407VG 配置）
- ✅ 复位控制（正常复位）
- ✅ 寄存器读取（R0、PC、SP）
- ✅ 断开连接

**测试通过的功能**:
- ✅ 设备连接和枚举
- ✅ 自动芯片检测（使用 STM32F407VG 配置）
- ✅ 复位控制（正常复位）
- ✅ 寄存器读取（R0、R15 (PC)、R13 (SP)、R14 (LR)）
- ✅ 目标电压读取
- ✅ CPU 暂停/运行控制
- ✅ 断开连接

**使用建议**:
```python
# 连接 FC7300
connect_device(interface="JTAG")

# 复位设备
reset_target(reset_type="normal")

# 读取寄存器
read_registers(register_names=["R0", "R15 (PC)", "R13 (SP)", "R14"])

# 获取目标电压
get_target_voltage()

# CPU 控制
halt_cpu()
run_cpu()
```

---

## 连接问题

### Q1: 连接失败，提示 "Unsupported device selected"

**A**: 目标芯片不在标准 JLink 设备列表中。

**解决方案**:
1. 使用 `list_flagchip_devices()` 查看支持的 Flagchip 设备
2. 如果是 Flagchip 芯片，指定芯片名称：
   ```
   connect_device(chip_name="FC4150F2MBSxXxxxT1A")
   ```
3. 如果不是 Flagchip 芯片，检查芯片型号并尝试类似设备

---

### Q2: 连接失败，提示 "Active read protection detected"

**A**: 芯片启用了读保护。

**解决方案**:
1. 使用 JLink Unlock 工具解除读保护
2. 或者使用解锁脚本（Flagchip 补丁中包含）
3. 联系芯片厂商获取解锁方法

---

### Q3: 连接失败，提示 "Unknown DEV_ID: 0x00000000"

**A**: 芯片 ID 无法识别，可能是：
- 芯片供电不足
- SWD/JTAG 连接问题
- 芯片型号不匹配

**解决方案**:
1. 检查目标芯片供电电压（3.3V）
2. 检查 SWD/JTAG 连接线
3. 尝试使用不同的接口（默认 JTAG，可尝试 SWD）：
   ```
   connect_device(interface="JTAG")  # 默认
   connect_device(interface="SWD")   # 备选
   ```
4. 尝试不同的芯片名称或使用简化名称

---

### Q4: 找不到 JLink 设备

**A**: list_jlink_devices() 返回空列表

**解决方案**:
1. 检查 JLink 是否连接到电脑
2. 检查 USB 驱动是否安装
3. 尝试重新插拔 JLink
4. 检查 JLink Manager 是否能识别设备

---

## 内存操作问题

### Q5: 读取内存失败

**A**: 可能的原因：
- 地址超出范围
- 芯片未连接
- 内存区域受保护

**解决方案**:
1. 确认设备已连接：`get_connection_status()`
2. 检查地址是否在有效范围内
3. 尝试读取 RAM 地址（如 0x20000000）

---

### Q6: 写入内存失败

**A**: 可能的原因：
- 地址是 Flash（Flash 需要特殊操作）
- 地址超出范围
- 内存区域受保护

**解决方案**:
1. 确认写入 RAM 地址
2. 如果要写入 Flash，使用 `program_flash()` 工具
3. 检查地址是否有效

---

## Flash 操作问题

### Q7: 烧录失败

**A**: 可能的原因：
- 文件格式不支持
- Flash 被锁定
- 文件路径错误

**解决方案**:
1. 确认文件格式（支持 .hex, .bin, .elf）
2. 使用绝对路径
3. 先擦除 Flash：`erase_flash()`
4. 检查 Flash 是否被锁定

---

### Q8: 校验失败

**A**: Flash 内容与文件不匹配

**解决方案**:
1. 重新烧录固件
2. 检查 Flash 是否损坏
3. 尝试擦除整个 Flash 后重新烧录

---

### Q9: 擦除失败

**A**: 可能的原因：
- Flash 被锁定
- 地址范围无效
- 设备未连接

**解决方案**:
1. 确认设备已连接
2. 尝试擦除整片：`erase_flash()`
3. 检查 Flash 是否被保护

---

## RTT 问题

### Q10: RTT 无法启动

**A**: 目标芯片可能没有实现 RTT 功能

**解决方案**:
1. 确认目标芯片代码中实现了 RTT
2. 检查 RTT 缓冲区配置
3. 确认 RTT 在目标芯片中已初始化

---

### Q11: RTT 读取不到数据

**A**: 可能的原因：
- RTT 未启动
- 目标芯片没有输出
- 缓冲区为空

**解决方案**:
1. 确认 RTT 已启动：`rtt_start()`
2. 确认目标芯片正在运行
3. 确认目标芯片有 RTT 输出

---

### Q12: RTT 写入无响应

**A**: 目标芯片可能没有实现 RTT 输入

**解决方案**:
1. 确认目标芯片实现了 RTT 输入通道
2. 检查 RTT 缓冲区配置
3. 确认目标芯片在处理输入

---

## GDB Server 问题

### Q13: GDB Server 无法启动

**A**: 端口可能被占用

**解决方案**:
1. 使用不同的端口：
   ```
   start_gdb_server(port=2332)
   ```
2. 检查端口是否被其他程序占用
3. 关闭其他 GDB Server 实例

---

### Q14: GDB 无法连接

**A**: 可能的原因：
- GDB Server 未启动
- 端口不匹配
- 防火墙阻止

**解决方案**:
1. 确认 GDB Server 已启动：`get_gdb_server_status()`
2. 使用正确的端口连接：
   ```
   target remote localhost:2331
   ```
3. 检查防火墙设置

---

## Flagchip 专用问题

### Q15: 支持设备名称智能匹配吗？

**A**: 是的！支持简化名称自动匹配到完整名称。

**智能匹配规则**:
- 简化名称：`FC7300F4MDD` → 完整名称：`FC7300F4MDDxXxxxT1C`
- 批次优先级：T1C > T1B > T1A，自动选择最新批次
- 自动排除：Unlock、Factory、FromRom 特殊版本

**示例**:
```
# 使用简化名称
connect_device(chip_name="FC7300F4MDD")
# 自动匹配到: FC7300F4MDDxXxxxT1C

# 匹配失败时提供建议
connect_device(chip_name="UNKNOWN")
# 返回相似设备列表
```

---

### Q16: 默认使用什么接口？

**A**: 默认使用 **JTAG** 接口。

**原因**:
- Flagchip 芯片（特别是 FC7300 系列）主要使用 JTAG 接口
- JTAG 支持多核调试和更好的信号质量
- 已验证 FC7300F4MDS/F4MDD 使用 JTAG 连接稳定

**如何切换接口**:
```
# 默认 JTAG（推荐）
connect_device(chip_name="FC7300F4MDD")

# 使用 SWD
connect_device(chip_name="FC7300F4MDD", interface="SWD")
```

---

### Q17: T1C、T1B、T1A 是什么意思？

**A**: 这些是芯片的批次版本号。

**版本含义**:
- **T1C**: 最新批次，通常功能最完整
- **T1B**: 较新批次
- **T1A**: 早期批次

**自动选择**:
- 系统自动选择最新批次（T1C 优先）
- 如果只有 T1B，则选择 T1B
- 如果只有 T1A，则选择 T1A

**示例**:
```
connect_device(chip_name="FC7300F4MDD")
# 自动选择: FC7300F4MDDxXxxxT1C (如果有 T1C)
# 或: FC7300F4MDDxXxxxT1B (如果没有 T1C)
```

---

### Q18: 如何选择正确的 Flagchip 芯片名称？

**A**: 
1. 使用简化名称，系统自动匹配：
   ```
   connect_device(chip_name="FC7300F4MDD")
   ```
2. 或使用 `list_flagchip_devices()` 查看所有支持的设备
3. 根据芯片型号选择：
   - FC4150 系列：F2MBSxXxxxT1A, F1MBSxXxxxT1A 等
   - FC7240 系列：F2MDSxXxxxT1A
   - FC7300 系列：F8MDQxXxxxT1B, F8MDTxXxxxT1B 等
4. 如果不确定，可以尝试自动检测：
   ```
   connect_device()
   ```

---

### Q19: Flagchip 芯片连接失败

**A**: 
1. 确认芯片名称正确（或使用简化名称让系统自动匹配）
2. 尝试不同的接口（默认 JTAG）：
   ```
   connect_device(interface="JTAG")
   ```
3. 检查芯片是否启用了读保护
4. 尝试使用解锁脚本
5. 查看连接失败的错误提示和设备建议

---

## 性能问题

### Q17: 操作速度慢

**A**: 可能的原因：
- SWD 速度设置过低
- Flash 操作速度慢
- 网络延迟（远程 JLink）

**解决方案**:
1. 增加 SWD 速度（在 JLink Manager 中设置）
2. Flash 操作本身较慢，属正常现象
3. 使用本地 USB 连接而非网络

---

### Q18: 频繁超时

**A**: 可能的原因：
- JLink 连接不稳定
- 目标芯片响应慢
- 网络延迟

**解决方案**:
1. 检查 JLink USB 连接
2. 重新连接 JLink
3. 增加超时时间（在配置中）

---

## 其他问题

### Q19: 如何查看详细日志？

**A**: 日志会输出到 stderr，包含详细的调试信息。

---

### Q20: 如何重置连接？

**A**: 
```
disconnect_device()
connect_device()
```

---

### Q21: 支持哪些芯片？

**A**: 
- 标准 JLink 支持的芯片（数百种）
- Flagchip 芯片（57种，通过补丁支持）
- 使用 `list_flagchip_devices()` 查看完整列表

---

### Q22: 如何同时连接多个设备？

**A**: 当前版本仅支持单设备连接。如需多设备，请：
1. 使用多个 JLink 设备
2. 分别运行多个 MCP 服务器实例

---

### Q23: 如何退出连接？

**A**: 
```
disconnect_device()
```

---

### Q24: RTT 和 GDB Server 能同时使用吗？

**A**: 可以。但需要注意：
- RTT 使用专用的 RTT 通道
- GDB Server 使用调试通道
- 两者不会冲突

---

### Q25: 如何更新 JLink 固件？

**A**: 
1. 下载 JLink Software from SEGGER
2. 运行 JLinkUpdater
3. 选择你的 JLink 设备
4. 更新固件

---

### Q26: 支持 RTT Trace 吗？

**A**: 当前版本不支持 RTT Trace。如需追踪功能，请使用 GDB Server。

---

### Q27: 如何备份 Flash 内容？

**A**: 
1. 读取 Flash：
   ```
   read_memory(address="0x08000000", size=flash_size)
   ```
2. 保存到文件

---

### Q28: 如何恢复出厂设置？

**A**: 使用芯片厂商提供的恢复工具或方法。

---

### Q29: 支持加密芯片吗？

**A**: 
- 可以连接加密芯片
- 但无法读取加密内容
- 可以烧录未加密的固件

---

### Q30: 如何获取技术支持？

**A**: 
1. 查看本 FAQ
2. 查看示例文档
3. 查看 API 文档
4. 联系芯片厂商或 SEGGER

---

## 故障排除流程

### 问题：无法连接

1. 检查 JLink 设备：`list_jlink_devices()`
2. 检查连接状态：`get_connection_status()`
3. 尝试不同的接口：`connect_device(interface="JTAG")`
4. 检查芯片供电：`get_target_voltage()`
5. 尝试指定芯片名称

### 问题：无法读取/写入

1. 确认设备已连接
2. 确认地址有效
3. 检查内存保护
4. 尝试不同的地址

### 问题：RTT 无输出

1. 确认 RTT 已启动：`rtt_start()`
2. 确认目标芯片运行中
3. 确认目标芯片有 RTT 实现
4. 检查 RTT 缓冲区配置

### 问题：Flash 操作失败

1. 确认设备已连接
2. 确认文件路径正确
3. 先擦除 Flash
4. 检查 Flash 是否被锁定