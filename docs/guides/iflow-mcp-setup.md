# 在任何 iFlow CLI 项目中使用 JLink MCP

本教程介绍如何将 JLink MCP 配置为全局可用，这样你可以在任何 iFlow CLI 项目中使用 JLink 调试功能。

## 目录

- [概述](#概述)
- [前提条件](#前提条件)
- [安装步骤](#安装步骤)
  - [方法一：使用 PowerShell 脚本（推荐）](#方法一使用-powershell-脚本推荐)
  - [方法二：手动编辑配置文件](#方法二手动编辑配置文件)
  - [方法三：使用命令行](#方法三使用命令行)
- [验证安装](#验证安装)
- [使用方法](#使用方法)
- [故障排除](#故障排除)
- [卸载](#卸载)

---

## 概述

通过将 JLink MCP 添加到 iFlow 的全局配置中，你可以：

- ✅ 在任何目录打开 iFlow CLI 都能使用 JLink 功能
- ✅ 不需要在每个项目重复配置
- ✅ 与项目级配置不冲突（可以同时存在）

---

## 前提条件

1. **已安装 iFlow CLI**
   ```bash
   iflow --version
   ```

2. **已安装 JLink MCP 项目依赖**
   ```bash
   cd C:\1.Projects\Can\jlink_mcp
   uv sync
   ```

3. **JLink 调试器已连接（可选，使用时需要）**

---

## 安装步骤

### 方法一：使用 PowerShell 脚本（推荐）

在 PowerShell 中执行以下脚本：

```powershell
# 定义配置文件路径
$configPath = "$env:USERPROFILE\.iflow\settings.json"

# 确保配置目录存在
if (-not (Test-Path "$env:USERPROFILE\.iflow")) {
    New-Item -ItemType Directory -Path "$env:USERPROFILE\.iflow" -Force
}

# 读取现有配置（如果不存在则创建空对象）
if (Test-Path $configPath) {
    $config = Get-Content $configPath -Raw | ConvertFrom-Json
} else {
    $config = @{}
}

# 确保 mcpServers 属性存在
if (-not $config.mcpServers) {
    $config | Add-Member -NotePropertyName "mcpServers" -NotePropertyValue @{} -Force
}

# 添加 JLink MCP 配置
$jlinkConfig = @{
    command = "python"
    args = @("-m", "jlink_mcp")
    cwd = "C:\1.Projects\Can\jlink_mcp"
    timeout = 60000
    trust = $true
}

# 如果已存在则覆盖
if ($config.mcpServers."jlink-mcp") {
    $config.mcpServers."jlink-mcp" = $jlinkConfig
    Write-Host "🔄 已更新 JLink MCP 配置"
} else {
    $config.mcpServers | Add-Member -NotePropertyName "jlink-mcp" -NotePropertyValue $jlinkConfig -Force
    Write-Host "✅ 已添加 JLink MCP 配置"
}

# 保存配置
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath

Write-Host "
配置完成！现在可以在任何 iFlow CLI 项目中使用 JLink MCP。
运行 '/mcp refresh' 刷新 MCP 列表。
"
```

### 方法二：手动编辑配置文件

1. **打开全局配置文件**
   
   文件位置：`%USERPROFILE%\.iflow\settings.json`
   
   在文件资源管理器地址栏输入：
   ```
   %USERPROFILE%\.iflow\
   ```

2. **编辑配置**

   在 `mcpServers` 部分添加以下内容：

   ```json
   {
     "mcpServers": {
       "jlink-mcp": {
         "command": "python",
         "args": ["-m", "jlink_mcp"],
         "cwd": "C:\\1.Projects\\Can\\jlink_mcp",
         "timeout": 60000,
         "trust": true
       }
     }
   }
   ```

3. **保存文件**

### 方法三：使用命令行

**在 CMD（命令提示符）中执行：**

```cmd
iflow mcp add-json --scope user jlink-mcp "{\"command\":\"python\",\"args\":[\"-m\",\"jlink_mcp\"],\"cwd\":\"C:\\1.Projects\\Can\\jlink_mcp\",\"timeout\":60000,\"trust\":true}"
```

**注意：** 必须在 CMD 中执行，PowerShell 会因转义问题失败。

---

## 验证安装

### 1. 命令行验证

```bash
# 列出所有 MCP 服务器
iflow mcp list
```

应该能看到 `jlink-mcp` 及其 30 个工具。

### 2. iFlow CLI 内验证

在任意目录打开 iFlow CLI，执行：

```
/mcp list
```

输出示例：
```
已安装的 MCP 服务器:

1. jlink-mcp
   工具数量: 30
   状态: ✅ 已连接
   
   可用工具:
   - list_jlink_devices
   - connect_to_device
   - disconnect_device
   - ...
```

### 3. 测试连接

在 iFlow CLI 中询问：

```
帮我列出连接的 JLink 设备
```

AI 会自动调用 `list_jlink_devices` 工具。

---

## 使用方法

### 场景 1：在新项目中调试

```bash
# 进入任意项目目录
cd C:\MyProject\firmware

# 打开 iFlow CLI
iflow

# 在 CLI 中直接询问
> 帮我连接 JLink 并读取芯片信息
```

### 场景 2：结合项目代码分析

```
> 查看这个项目的固件代码，帮我检查是否有内存泄漏问题
> 连接 JLink 读取当前设备的内存使用情况
> 对比分析一下
```

### 场景 3：远程协助调试

```
> 我现在在客户现场，设备是 FC7300F4MDSXXXXXT1C
> 帮我连接并读取错误日志
> 分析一下可能的问题原因
```

---

## 故障排除

### 问题 1：MCP 服务器未找到

**现象：**
```
/mcp list
# 没有显示 jlink-mcp
```

**解决：**
```
/mcp refresh
```

或重启 iFlow CLI。

### 问题 2：连接超时

**现象：**
```
工具调用超时
```

**解决：**

1. 检查 JLink 调试器是否连接
2. 增加超时时间：
   ```json
   {
     "timeout": 120000
   }
   ```

### 问题 3：找不到 Python 模块

**现象：**
```
ModuleNotFoundError: No module named 'jlink_mcp'
```

**解决：**

确保在 jlink_mcp 项目目录中运行过：

```bash
cd C:\1.Projects\Can\jlink_mcp
uv sync
```

或使用虚拟环境的 Python：

```json
{
  "command": "C:\\1.Projects\\Can\\jlink_mcp\\.venv\\Scripts\\python.exe"
}
```

### 问题 4：Windows 执行策略限制

**现象：**
```
File iflow.ps1 cannot be loaded because running scripts is disabled
```

**解决：**

使用 CMD 代替 PowerShell：

```cmd
iflow mcp add-json ...
```

或在 PowerShell 中临时放宽策略：

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 卸载

### 命令行卸载

```bash
iflow mcp remove jlink-mcp --scope user
```

### 手动卸载

编辑 `%USERPROFILE%\.iflow\settings.json`，删除 `jlink-mcp` 部分。

---

## 配置参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | ✅ | 启动命令，这里是 `python` |
| `args` | array | ✅ | 命令参数，`["-m", "jlink_mcp"]` 表示运行模块 |
| `cwd` | string | ✅ | 工作目录，MCP 服务器运行的位置 |
| `timeout` | number | ❌ | 超时时间（毫秒），默认 30000 |
| `trust` | boolean | ❌ | 是否信任该服务器，跳过确认提示 |
| `env` | object | ❌ | 环境变量配置 |

---

## 相关链接

- [快速开始](./quickstart.md) - 项目安装和基本使用
- [API 文档](../reference/api.md) - 所有工具详细说明
- [使用示例](../reference/examples.md) - 实际使用场景示例
- [常见问题](../reference/faq.md) - FAQ 和故障排除

---

## 总结

通过全局配置 JLink MCP，你现在可以在任何 iFlow CLI 会话中使用 JLink 调试功能，无需重复配置。

**核心要点：**

1. 全局配置位于 `%USERPROFILE%\.iflow\settings.json`
2. 配置后运行 `/mcp refresh` 刷新
3. 使用 `iflow mcp list` 验证安装
4. 任何项目都可以直接调用 JLink 工具

如有问题，请参考[常见问题](../reference/faq.md)或提交 Issue。
