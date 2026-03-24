# JLink MCP 常见问题解答 (FAQ)

## 连接问题

### Q1: 连接失败，提示 "Unsupported device"

**A**: 芯片不在标准 JLink 设备列表中。

**解决方案**:
1. 使用 `list_device_patches()` 查看支持的补丁
2. 指定芯片名称：`connect_device(chip_name="FC7300F4MDD")`
3. 使用 `match_chip_name()` 验证名称

---

### Q2: 提示 "Active read protection detected"

**A**: 芯片启用了读保护。

**解决方案**: 使用 JLink Unlock 工具解除读保护。

---

### Q3: 提示 "Unknown DEV_ID: 0x00000000"

**A**: 芯片 ID 无法识别，可能原因：
- 芯片供电不足
- SWD/JTAG 连接问题
- 芯片型号不匹配

**解决方案**:
1. 检查目标芯片供电电压（3.3V）
2. 检查 SWD/JTAG 连接线
3. 尝试不同接口：`connect_device(interface="JTAG")`

---

### Q4: 找不到 JLink 设备

**A**: `list_jlink_devices()` 返回空列表。

**解决方案**:
1. 检查 JLink USB 连接
2. 检查 JLink 驱动是否安装
3. 尝试重新插拔 JLink

---

## 内存操作问题

### Q5: 读取内存失败

**A**: 可能原因：
- 地址超出范围
- 芯片未连接
- 内存区域受保护

**解决方案**:
1. 确认设备已连接：`get_connection_status()`
2. 检查地址是否在有效范围内
3. 尝试读取 RAM 地址（如 0x20000000）

---

### Q6: 写入内存失败

**A**: 可能原因：
- 地址是 Flash（需要特殊操作）
- 地址超出范围
- 内存区域受保护

**解决方案**:
1. 确认写入 RAM 地址
2. 如果写入 Flash，使用 `program_flash()`

---

## Flash 操作问题

### Q7: 烧录失败

**A**: 可能原因：
- 数据格式不正确
- Flash 被锁定
- 地址错误

**解决方案**:
1. 确认数据格式为 bytes 类型
2. 先擦除 Flash：`erase_flash(chip_erase=True)`
3. 检查 Flash 是否被锁定

---

### Q8: 校验失败

**A**: Flash 内容与数据不匹配。

**解决方案**:
1. 重新烧录固件
2. 尝试擦除整个 Flash 后重新烧录

---

## RTT 问题

### Q9: RTT 无法启动

**A**: 目标芯片可能没有实现 RTT 功能。

**解决方案**:
1. 确认目标芯片代码中实现了 RTT
2. 检查 RTT 缓冲区配置
3. 确认 RTT 在目标芯片中已初始化

---

### Q10: RTT 读取不到数据

**A**: 可能原因：
- RTT 未启动
- 目标芯片没有输出
- 缓冲区为空

**解决方案**:
1. 确认 RTT 已启动：`rtt_start()`
2. 确认目标芯片正在运行
3. 确认目标芯片有 RTT 输出

---

## GDB Server 问题

### Q11: GDB Server 无法启动

**A**: 端口可能被占用。

**解决方案**:
1. 使用不同端口：`start_gdb_server(port=2332)`
2. 检查端口是否被占用
3. 关闭其他 GDB Server 实例

---

### Q12: GDB 无法连接

**A**: 可能原因：
- GDB Server 未启动
- 端口不匹配
- 防火墙阻止

**解决方案**:
1. 确认 GDB Server 已启动：`get_gdb_server_status()`
2. 使用正确端口：`target remote localhost:2331`
3. 检查防火墙设置

---

## Flagchip 专用问题

### Q13: 支持芯片名称智能匹配吗？

**A**: 是的。支持简化名称自动匹配。

**示例**:
```
connect_device(chip_name="FC7300F4MDD")
# 自动匹配到: FC7300F4MDDxXxxxT1C
```

**匹配规则**:
- 前缀匹配
- 批次优先级：T1C > T1B > T1A
- 排除特殊版本：Unlock/Factory/FromRom

---

### Q14: 默认使用什么接口？

**A**: 默认使用 **JTAG** 接口。

**切换接口**:
```
connect_device(chip_name="FC7300F4MDD", interface="SWD")
```

---

### Q15: T1C、T1B、T1A 是什么意思？

**A**: 芯片的批次版本号。

- **T1C**: 最新批次
- **T1B**: 较新批次
- **T1A**: 早期批次

系统自动选择最新批次。

---

### Q16: 如何选择正确的 Flagchip 芯片名称？

**A**:
1. 使用简化名称，系统自动匹配
2. 使用 `list_device_patches()` 查看所有支持的设备
3. 根据芯片型号选择（FC4150/FC7240/FC7300 系列）
4. 如果不确定，可以尝试自动检测

---

## SVD 问题

### Q17: 什么是 SVD？

**A**: SVD (System View Description) 是 ARM 定义的硬件描述文件格式，用于描述芯片的外设和寄存器结构。

**用途**:
- 解析寄存器字段含义
- 显示外设地址映射
- 调试时查看寄存器状态

---

### Q18: 如何查看支持的 SVD 设备？

**A**: `list_svd_devices()`

---

### Q19: SVD 设备列表为空？

**A**:
1. 检查 `.svd_cache` 目录是否存在 SVD 文件
2. 下载对应芯片的 SVD 文件

---

## 使用指南问题

### Q20: 如何获取工具使用指南？

**A**:
```
get_usage_guidance()
get_usage_guidance(category="connection")
```

---

### Q21: 如何获取最佳实践？

**A**: `get_best_practices(task_type="connect_device")`

---

### Q22: 如何查看禁止的操作？

**A**: `get_forbidden_operations()`

---

## 故障排除流程

### 无法连接

1. `list_jlink_devices()` - 检查设备
2. `get_connection_status()` - 检查状态
3. 尝试不同接口
4. `get_target_voltage()` - 检查供电

### 无法读取/写入

1. 确认设备已连接
2. 确认地址有效
3. 检查内存保护
4. 尝试不同地址

### Flash 操作失败

1. 确认设备已连接
2. 确认数据格式正确
3. 先擦除 Flash
4. 检查 Flash 锁定

---

## 调试错误

### Q23: 目标正在运行错误

**A**: 尝试操作时目标正在运行。

**解决方案**: 先调用 `halt_cpu()` 暂停目标。

---

### Q24: 操作超时

**A**: 目标响应慢或连接不稳定。

**解决方案**:
1. 复位目标后重试
2. 检查连接线路
3. 降低接口速度

---

## 最佳实践

### Q25: 如何确保安全操作？

**A**:
1. 操作前检查连接状态
2. 内存操作前暂停 CPU
3. Flash 操作前先擦除
4. 操作完成后断开连接

### Q26: 如何提高调试效率？

**A**:
1. 使用 `match_chip_name()` 验证芯片名称
2. 使用 SVD 工具解析寄存器
3. 使用 RTT 获取实时日志
4. 使用 GDB Server 配合 IDE

---

## 性能问题

### Q27: 内存读取速度慢

**A**: 可能原因：
- 读取数据量过大
- 接口速度设置过低
- JTAG 模式比 SWD 慢

**解决方案**:
1. 减少单次读取大小
2. 尝试使用 SWD 接口
3. 提高接口速度：`connect_device(chip_name="...", speed=12000)`

### Q28: Flash 烧录时间长

**A**: 正常现象，Flash 烧录比内存操作慢。

**优化建议**:
1. 仅擦除需要的区域
2. 使用更高的接口速度
3. 确保数据格式正确，避免重试

---

## 兼容性问题

### Q29: 支持 Linux/Mac 吗？

**A**: 支持。但需要：
1. 安装 JLink 驱动
2. 配置 USB 权限（Linux）
3. 确保 pylink-square 库正确安装

### Q30: 支持哪些 JLink 型号？

**A**: 支持所有 SEGGER JLink 型号：
- J-Link BASE
- J-Link PLUS
- J-Link ULTRA+
- J-Link PRO
- J-Link EDU

### Q31: 支持哪些芯片厂商？

**A**:
- **内置支持**：ST、NXP、TI、Microchip 等主流厂商
- **补丁支持**：Flagchip（FC4150/FC7240/FC7300 系列）
- 可通过 `list_device_patches()` 查看已加载的补丁

---

## 使用技巧

### Q32: 如何快速验证连接？

**A**:
```
# 一键验证
connect_device(chip_name="FC7300F4MDD")
get_target_voltage()  # 检查电压
disconnect_device()
```

### Q33: 如何查看支持的芯片列表？

**A**:
```
list_device_patches()  # 补丁设备列表
list_svd_devices()     # SVD 设备列表
```

### Q34: 如何批量操作多个芯片？

**A**: 串行连接和断开：
```
for chip in ["FC7300F4MDD", "FC4150F1MBS"]:
    connect_device(chip_name=chip)
    # 执行操作...
    disconnect_device()
```

---

## 高级问题

### Q35: 如何添加新的设备补丁？

**A**:
1. 创建插件文件：`src/jlink_mcp/plugins/xxx_patch.py`
2. 实现 `DevicePatchInterface` 接口
3. 在 `device_patch_manager.py` 中注册
4. 添加 ELF 文件到 `resources/` 目录

### Q36: 如何添加新的 SVD 文件？

**A**:
1. 获取芯片的 SVD 文件
2. 放置到 `src/jlink_mcp/.svd_cache/` 目录
3. 重启 MCP 服务器
4. 使用 `list_svd_devices()` 验证

### Q37: 如何自定义错误处理？

**A**: 所有错误都有标准格式：
```python
result = some_tool()
if not result['success']:
    error_code = result['error']['code']
    error_desc = result['error']['description']
    # 自定义处理...
```

### Q38: 如何实现自动化测试？

**A**: 使用 pytest + mock：
```python
def test_connect(mocker):
    mocker.patch('jlink_mcp.jlink_manager.JLinkManager.connect')
    result = connect_device(chip_name="FC7300F4MDD")
    assert result['success'] == True
```

### Q39: 如何调试 MCP 服务器本身？

**A**:
1. 启动时添加日志：`python -m jlink_mcp --debug`
2. 查看 `jlink_manager.py` 中的日志输出
3. 使用 `get_connection_status()` 检查内部状态

### Q40: 如何贡献代码？

**A**:
1. Fork 项目仓库
2. 创建功能分支
3. 提交 Pull Request
4. 等待代码审查

---

## 获取帮助

1. 查看 [API 文档](./api.md)
2. 查看 [使用示例](./examples.md)
3. 查看 [架构文档](../ARCHITECTURE.md)
4. 提交 GitHub Issue
