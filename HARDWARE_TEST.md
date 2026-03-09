# JLink MCP 硬件测试指南

本目录包含用于验证 JLink MCP 服务器功能的硬件测试脚本。

## 测试脚本

### 1. test_hardware_simple.py - 简化测试脚本

快速测试核心功能，适合日常验证。

**测试内容：**
- 列出 JLink 设备
- 连接/断开设备
- 获取连接状态和目标信息
- 读取 CPU 寄存器
- 列出 Flagchip 设备
- 列出 SVD 设备
- 获取外设列表
- 解析寄存器值

**运行方法：**
```bash
python test_hardware_simple.py
# 或使用虚拟环境
.venv\Scripts\python.exe test_hardware_simple.py
```

### 2. test_hardware_comprehensive.py - 全面测试脚本

完整的测试套件，涵盖所有功能模块。

**测试内容：**
- 连接管理（4 个测试）
- 设备信息（4 个测试）
- 内存操作（4 个测试）
- 调试控制（7 个测试）
- SVD 功能（5 个测试）
- Flash 操作（3 个测试，默认禁用）
- RTT 功能（5 个测试，默认禁用）
- GDB Server（3 个测试，默认禁用）

**运行方法：**
```bash
python test_hardware_comprehensive.py
# 或使用虚拟环境
.venv\Scripts\python.exe test_hardware_comprehensive.py
```

**配置选项：**
编辑 `TEST_CONFIG` 变量来调整测试选项：
- `test_flash`: Flash 操作测试（需要固件文件）
- `test_rtt`: RTT 功能测试（需要目标程序支持）
- `test_gdb`: GDB Server 测试
- `test_svd`: SVD 功能测试
- `test_breakpoints`: 断点测试
- `test_memory_write`: 内存写入测试

## 测试要求

### 硬件要求
- J-Link 调试器（已测试：J-Link V11）
- 目标芯片（已测试：FC7300F4MDSXXXXXT1C）
- USB 连接线

### 软件要求
- Python 3.10+
- 已安装项目依赖（参考 `requirements-uv.txt`）

## 已知问题

### JLink 设备占用

如果遇到 "J-Link is already open" 错误：

1. **关闭其他 JLink 应用**
   - 关闭 J-Link Commander
   - 关闭 JLinkGDBServer
   - 关闭 IDE（如 Keil, IAR, Segger Embedded Studio）

2. **手动重置 JLink**
   - 拔掉 JLink USB 连接线
   - 等待 5 秒
   - 重新插入 USB

3. **使用 JLink Commander 关闭连接**
   ```
   JLinkExe
   > exit
   ```

4. **在 Windows 任务管理器中结束进程**
   - 查找 `JLink.exe` 或 `JLinkGDBServer.exe`
   - 结束相关进程

### 目标电压读取失败

这是 pylink-square 库的限制，不影响其他功能。

## 测试结果解读

测试结果会显示：
- ✅ 测试通过
- ❌ 测试失败
- ⏭️  测试跳过

最后会输出汇总信息：
- 总计测试数
- 通过数
- 失败数
- 跳过数
- 失败详情

## 已验证的功能

### FC7300F4MDSXXXXXT1C (Flagchip)
- ✅ 设备连接
- ✅ 复位控制
- ✅ 寄存器读取
- ✅ 断开连接
- ✅ SVD 文件加载（11 个设备）
- ✅ 外设查询（FLEXCAN0: 59 个寄存器）
- ✅ 寄存器字段解析

## 扩展测试

### 添加新的芯片型号

编辑测试配置中的 `devices` 数组：
```python
"devices": [
    {
        "name": "FC7300F4MDSxXxxxT1C",
        "serial_number": "941000024",
        "interface": "JTAG",
        "chip_name": None,  # 或指定芯片名称
    },
    # 添加更多设备...
],
```

### 添加新的测试用例

在相应的 `test_*` 函数中添加测试逻辑。

## 故障排除

### 导入错误
确保 Python 路径正确：
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
```

### 设备未找到
- 检查 USB 连接
- 检查 JLink 驱动是否正确安装
- 尝试不同的 USB 端口

### 连接超时
- 检查目标芯片供电
- 检查调试接口连接（JTAG/SWD）
- 尝试降低接口速度

## 报告问题

如果测试失败，请提供：
1. 错误信息
2. JLink 型号和固件版本
3. 目标芯片型号
4. 测试脚本输出