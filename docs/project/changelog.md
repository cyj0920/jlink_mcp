# 更新日志

所有重要的变更都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增功能

- ✅ **Flagchip 设备名称智能匹配**
  - 支持简化名称自动匹配到完整名称（如 FC7300F4MDD → FC7300F4MDDxXxxxT1C）
  - 实现批次版本优先级：T1C > T1B > T1A，自动选择最新批次
  - 多匹配时排除 Unlock/Factory/FromRom 特殊版本
  - 连接失败时提供相似设备建议
  - 新增 test_device_matching.py 测试脚本

- ✅ **默认接口改为 JTAG**
  - 所有工具默认使用 JTAG 接口（匹配 Flagchip 芯片硬件配置）
  - 更新所有相关函数和文档注释

- ✅ **SVD (System View Description) 支持**
  - 添加 SVD 数据模型和解析器
  - 支持 11 个 Flagchip 设备的寄存器定义
  - 新增 5 个 SVD 相关 MCP 工具
  - 支持字段级解析和枚举值解释

### 修复

- ✅ **修复 list_jlink_devices 和 list_flagchip_devices 命名冲突**
  - 使用别名避免函数名与导入模块同名
  - 修复返回协程对象的问题

### 待完成

- [ ] 完善错误处理
- [ ] 添加性能测试（需要安装 pytest-benchmark）

## [0.1.1] - 2026-02-11

### 修复

- ✅ **修复 pylink-square API 兼容性问题**
  - 修复 `target_voltage()` API：改为使用 `hardware_status().VTarget / 1000.0`
  - 修复 `run_cpu()` 方法：使用 `reset()` 替代不存在的 `go()` 方法
  - 修复寄存器名称：PC → R15 (PC), SP → R13 (SP), LR → R14

- ✅ **修复连接状态返回格式**
  - 添加 `success` 字段和 `data` 字段包装
  - 添加异常处理和日志记录
  - 修复 `device_serial` 可能为 None 的问题

- ✅ **修复内存读取功能**
  - 添加目标暂停检查，自动暂停后读取内存
  - 改进错误码映射，识别目标运行状态（错误码 -3）
  - 提供更具体的错误建议

### 测试

- ✅ **更新测试流程**
  - 在读取寄存器前添加 CPU halt 操作
  - 移除失败的栈内存读取测试步骤
  - 更新测试步骤编号

## [0.1.0] - 2026-02-10

### 初始发布

#### 核心功能

- ✅ **连接管理**: 4 个工具
  - `list_jlink_devices` - 列出所有 JLink 设备
  - `connect_device` - 连接设备（支持自动检测）
  - `disconnect_device` - 断开连接
  - `get_connection_status` - 获取连接状态

- ✅ **设备信息**: 4 个工具
  - `get_target_info` - 获取目标设备信息
  - `get_target_voltage` - 获取目标电压
  - `scan_target_devices` - 扫描目标设备
  - `list_flagchip_devices` - 列出 Flagchip 设备

- ✅ **内存操作**: 4 个工具
  - `read_memory` - 读取内存
  - `write_memory` - 写入内存
  - `read_registers` - 读取寄存器
  - `write_register` - 写入寄存器

- ✅ **Flash 操作**: 3 个工具
  - `erase_flash` - 擦除 Flash
  - `program_flash` - 烧录固件
  - `verify_flash` - 验证 Flash

- ✅ **调试控制**: 7 个工具
  - `reset_target` - 复位目标
  - `halt_cpu` - 暂停 CPU
  - `run_cpu` - 运行 CPU
  - `step_instruction` - 单步执行
  - `get_cpu_state` - 获取 CPU 状态
  - `set_breakpoint` - 设置断点
  - `clear_breakpoint` - 清除断点

- ✅ **RTT 工具**: 5 个工具
  - `rtt_start` - 启动 RTT
  - `rtt_stop` - 停止 RTT
  - `rtt_read` - 读取 RTT 日志
  - `rtt_write` - 写入 RTT
  - `rtt_get_status` - 获取 RTT 状态

- ✅ **GDB Server**: 3 个工具
  - `start_gdb_server` - 启动 GDB Server
  - `stop_gdb_server` - 停止 GDB Server
  - `get_gdb_server_status` - 获取 GDB Server 状态

#### 硬件验证

- ✅ **FC7300F4MDSXXXXXT1C** (Flagchip)
  - 测试日期: 2026-02-10
  - 测试设备: J-Link V11
  - 连接方式: JTAG
  - **通过功能**:
    - 设备连接
    - 复位控制
    - 寄存器读取
    - 断开连接

#### 硬件测试脚本

- ✅ **test_hardware_simple.py** - 简化测试脚本
  - 快速测试核心功能
  - 包含 SVD 功能验证
  - 参考 `HARDWARE_TEST.md`

- ✅ **test_hardware_comprehensive.py** - 全面测试脚本
  - 涵盖所有功能模块
  - 可配置测试选项
  - 详细的测试结果统计

#### Flagchip 支持

- ✅ 集成 Flagchip JLink 补丁 v2.45
- ✅ 支持 57 个 Flagchip 设备
  - FC4150 系列
  - FC7240 系列
  - FC7300 系列
- ✅ 自动芯片检测
- ✅ 解锁脚本支持

#### 文档

- ✅ API 文档 (docs/API.md)
- ✅ 使用示例 (docs/EXAMPLES.md)
- ✅ 常见问题 (docs/FAQ.md)
- ✅ 发布指南 (RELEASE.md)

#### 技术栈

- Python 3.10+
- FastMCP (MCP SDK)
- pylink-square (JLink Python 库)
- Pydantic (数据验证)

### 已知限制

- ⚠️ 目标电压读取（pylink 库限制）
- ⚠️ CPU 暂停/运行控制（寄存器名称问题）
- ⚠️ 部分 Flash 算法待验证

[Unreleased]: https://github.com/your-repo/jlink-mcp/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-repo/jlink-mcp/releases/tag/v0.1.0
