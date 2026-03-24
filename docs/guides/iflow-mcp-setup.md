# 在任何 iFlow CLI 项目中使用 JLink MCP

本教程介绍如何将 JLink MCP 配置为全局可用。

## 概述

通过将 JLink MCP 添加到 iFlow 的全局配置中，你可以：

- 在任何目录打开 iFlow CLI 都能使用 JLink 功能
- 不需要在每个项目重复配置
- 与项目级配置不冲突

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

3. **JLink 调试器已连接（可选）**

---

## 安装步骤

### 方法一：使用 PowerShell 脚本

在 PowerShell 中执行：

```powershell
# 定义配置文件路径
$configPath = "$env:USERPROFILE\.iflow\settings.json"

# 确保配置目录存在
if (-not (Test-Path "$env:USERPROFILE\.iflow")) {
    New-Item -ItemType Directory -Path "$env:USERPROFILE\.iflow" -Force
}

# 读取现有配置
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

$config.mcpServers | Add-Member -NotePropertyName "jlink-mcp" -NotePropertyValue $jlinkConfig -Force

# 保存配置
$config | ConvertTo-Json -Depth 10 | Set-Content $configPath
```

### 方法二：手动编辑配置文件

1. 打开全局配置文件：
   ```
   %USERPROFILE%\.iflow\settings.json
   ```

2. 添加配置：
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

### 方法三：使用命令行（CMD）

```cmd
iflow mcp add-json --scope user jlink-mcp "{\"command\":\"python\",\"args\":[\"-m\",\"jlink_mcp\"],\"cwd\":\"C:\\1.Projects\\Can\\jlink_mcp\",\"timeout\":60000,\"trust\":true}"
```

---

## 验证安装

### 1. 命令行验证

```bash
iflow mcp list
```

应该能看到 `jlink-mcp` 及其 41 个工具。

### 2. iFlow CLI 内验证

```
/mcp list
```

### 3. 测试连接

在 iFlow CLI 中询问：
```
帮我列出连接的 JLink 设备
```

---

## 使用方法

### 场景 1：在新项目中调试

```bash
cd C:\MyProject\firmware
iflow
# 直接询问：帮我连接 JLink 并读取芯片信息
```

### 场景 2：结合项目代码分析

```
查看这个项目的固件代码，帮我检查是否有内存泄漏问题
连接 JLink 读取当前设备的内存使用情况
对比分析一下
```

---

## 故障排除

### 问题 1：MCP 服务器未找到

**解决：** `/mcp refresh` 或重启 iFlow CLI

### 问题 2：连接超时

**解决：** 增加超时时间配置
```json
{
  "timeout": 120000
}
```

### 问题 3：找不到 Python 模块

**解决：** 使用虚拟环境的 Python：
```json
{
  "command": "C:\\1.Projects\\Can\\jlink_mcp\\.venv\\Scripts\\python.exe"
}
```

### 问题 4：JLink 设备未找到

**解决：**
1. 检查 JLink USB 连接
2. 安装 JLink 驱动
3. 在 iFlow CLI 中执行：`帮我列出 JLink 设备`

### 问题 5：芯片连接失败

**解决：**
1. 检查目标芯片供电
2. 检查 SWD/JTAG 连接线
3. 尝试不同接口：`connect_device(interface="SWD")`

### 问题 6：权限错误

**解决：**
1. 以管理员身份运行 iFlow CLI
2. 检查项目目录权限

### 问题 7：服务器启动后立即退出

**解决：**
1. 手动测试：`python -m jlink_mcp`
2. 检查依赖是否完整：`pip install -e .`
3. 查看错误日志

---

## 配置参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `command` | string | ✅ | 启动命令 |
| `args` | array | ✅ | 命令参数 |
| `cwd` | string | ✅ | 工作目录 |
| `timeout` | number | ❌ | 超时时间（毫秒） |
| `trust` | boolean | ❌ | 是否信任该服务器 |

### 高级配置选项

#### 多环境配置

可以为不同环境创建多个配置：

```json
{
  "mcpServers": {
    "jlink-mcp-dev": {
      "command": ".venv\\Scripts\\python.exe",
      "args": ["-m", "jlink_mcp", "--debug"],
      "cwd": "C:\\dev\\jlink_mcp"
    },
    "jlink-mcp-prod": {
      "command": "python",
      "args": ["-m", "jlink_mcp"],
      "cwd": "C:\\prod\\jlink_mcp"
    }
  }
}
```

#### 环境变量传递

```json
{
  "mcpServers": {
    "jlink-mcp": {
      "command": "python",
      "args": ["-m", "jlink_mcp"],
      "cwd": "C:\\1.Projects\\Can\\jlink_mcp",
      "env": {
        "JLINK_SVD_DIR": "C:\\svd_files",
        "JLINK_DEFAULT_INTERFACE": "SWD"
      }
    }
  }
}
```

#### 超时和重试配置

```json
{
  "mcpServers": {
    "jlink-mcp": {
      "timeout": 120000,
      "retryCount": 3,
      "retryDelay": 1000
    }
  }
}
```

---

## 卸载

```bash
iflow mcp remove jlink-mcp --scope user
```

或手动编辑配置文件删除 `jlink-mcp` 部分。

---

## 常见问题

### Q: MCP 服务器启动失败

**A**: 检查 Python 路径是否正确，确保虚拟环境已激活。

### Q: 工具列表为空

**A**: 运行 `/mcp refresh` 刷新。

### Q: 超时错误

**A**: 增加 `timeout` 配置值。

---

## 相关链接

- [快速开始](./quickstart.md)
- [API 文档](../reference/api.md)
- [使用示例](../reference/examples.md)