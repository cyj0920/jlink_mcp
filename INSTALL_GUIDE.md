# JLink MCP 安装指南

## 安装位置

JLink MCP 已成功安装到：`C:\Users\qxw0112\.iflow`

**重要**：现在可以从任何目录使用，不再受限于原始项目目录。

## 安装内容

### 主要组件
- `jlink_mcp/` - 主要包代码
- `jlink_mcp/tool/` - 资源文件（包含在包内）
  - `JLink_Patch_v2.45/` - Flagchip 设备补丁
  - `SVD_V1.5.6/` - SVD 寄存器定义文件
- `bin/jlink-mcp.exe` - 可执行文件
- `jlink_mcp_requirements.txt` - 依赖列表

### 依赖包
所有必要的依赖都已安装：
- pylink-square>=2.0.0
- mcp>=1.26.0
- pydantic>=2.12.0
- pydantic-settings>=2.12.0
以及它们的传递依赖

## MCP 服务器配置

### 自动配置

如果在 iflow 中使用，配置文件已自动更新为：

```json
{
  "command": "python",
  "args": ["-m", "jlink_mcp"],
  "timeout": 60000,
  "trust": true,
  "env": {
    "PYTHONPATH": "C:\\Users\\qxw0112\\.iflow"
  }
}
```

### 手动配置

如果需要手动配置 MCP 服务器：

1. 打开 iflow 设置文件：`C:\Users\qxw0112\.iflow\settings.json`
2. 找到 `mcpServers.jlink-mcp` 配置项
3. 确保配置如下：

```json
{
  "mcpServers": {
    "jlink-mcp": {
      "command": "python",
      "args": ["-m", "jlink_mcp"],
      "timeout": 60000,
      "trust": true,
      "env": {
        "PYTHONPATH": "C:\\Users\\qxw0112\\.iflow"
      }
    }
  }
}
```

4. 重启 iflow 使配置生效

**关键点**：
- 移除了 `cwd` 配置，使其可以在任何目录运行
- 添加了 `env.PYTHONPATH` 指向安装目录
- 这样无论在哪个项目目录启动 iflow，jlink-mcp 都能正常工作

## 使用方法

### 1. 在 iflow 中使用（推荐）

配置完成后，在 iflow 中：
1. 重启 iflow
2. jlink-mcp 服务器会自动启动
3. 在任何项目目录下都可以使用

检查服务器状态：
- 打开 iflow → 服务器管理
- jlink-mcp 应该显示为 🟢 Connected

### 2. 在 Python 脚本中使用

```python
import sys
sys.path.insert(0, r'C:\Users\qxw0112\.iflow')

from jlink_mcp.svd_manager import svd_manager
from jlink_mcp.flagchip_patch import flagchip_patch

# 检查可用性
print(f"SVD 可用: {svd_manager.is_available()}")
print(f"Flagchip 可用: {flagchip_patch.is_available()}")

# 获取支持的设备
devices = svd_manager.device_names
print(f"支持的 SVD 设备: {devices}")
```

### 2. 使用可执行文件

```bash
C:\Users\qxw0112\.iflow\bin\jlink-mcp.exe
```

### 3. 作为 MCP 服务器使用

需要设置环境变量 `PYTHONPATH`：

```powershell
$env:PYTHONPATH = "C:\Users\qxw0112\.iflow"
```

## 功能验证

运行以下命令验证安装：

```powershell
$env:PYTHONPATH="C:\Users\qxw0112\.iflow"
python -c "import sys; sys.path.insert(0, 'C:\\Users\\qxw0112\\.iflow'); from jlink_mcp.svd_manager import svd_manager; from jlink_mcp.flagchip_patch import flagchip_patch; print('SVD 设备:', len(svd_manager.device_names)); print('Flagchip 设备:', len(flagchip_patch.device_names))"
```

预期输出：
```
SVD 设备: 11
Flagchip 设备: 57
```

## 注意事项

1. **依赖冲突**：当前安装的 cryptography 版本可能与 pyopenssl 有冲突，但这不影响 JLink MCP 的主要功能。

2. **路径设置**：
   - MCP 服务器配置中已设置 `PYTHONPATH`，无需手动设置
   - 在 Python 脚本中使用时，需要手动添加到 `sys.path`

3. **资源文件**：所有必要的资源文件（SVD 和 Flagchip 补丁）都已包含在包内，无需额外配置。

4. **跨目录使用**：
   - ✅ 可以在任何目录启动 iflow
   - ✅ MCP 服务器会自动找到安装的包
   - ✅ 不受限于原始项目目录

5. **配置持久化**：
   - MCP 配置保存在 `C:\Users\qxw0112\.iflow\settings.json`
   - 重启 iflow 后配置自动生效
   - 无需每次手动设置环境变量

## 更新安装

如需更新，重新构建 wheel 并安装：

```powershell
cd C:\1.Projects\Can\jlink_mcp
python -m build --wheel
python -m pip install dist\jlink_mcp-0.1.0-py3-none-any.whl --target "C:\Users\qxw0112\.iflow" --no-deps
```

## 问题排查

### MCP 服务器无法连接

**症状**：jlink-mcp 显示 🔴 Disconnected

**解决方案**：
1. 检查配置文件：`C:\Users\qxw0112\.iflow\settings.json`
2. 确认 `mcpServers.jlink-mcp.env.PYTHONPATH` 设置正确
3. 重启 iflow
4. 检查日志输出是否有错误信息

### 导入错误
如果遇到模块导入错误，检查 `PYTHONPATH` 设置：

```powershell
echo $env:PYTHONPATH
```

### 资源文件错误
如果 SVD 或 Flagchip 补丁不可用，检查文件是否存在：

```powershell
Test-Path "C:\Users\qxw0112\.iflow\jlink_mcp\tool\SVD_V1.5.6"
Test-Path "C:\Users\qxw0112\.iflow\jlink_mcp\tool\JLink_Patch_v2.45"
```

## 技术支持

如有问题，请检查：
1. Python 版本 >= 3.10
2. 所有依赖是否正确安装
3. 环境变量设置是否正确
4. MCP 配置文件是否正确

## 架构改进

本次重构实现了以下改进：

### 1. 包内资源文件
- 将 `tool/` 目录从项目根目录移到 `src/jlink_mcp/tool/`
- 资源文件随包一起分发，无需额外配置
- 支持独立部署到任意目录

### 2. 路径引用优化
- `svd_manager.py`：使用包内路径 `Path(__file__).parent / "tool"`
- `flagchip_patch.py`：使用包内路径 `Path(__file__).parent / "tool"`
- 不再依赖项目根目录

### 3. MCP 配置优化
- 移除 `cwd` 限制
- 添加 `env.PYTHONPATH` 配置
- 支持从任何目录启动

### 4. 部署灵活性
- ✅ 可以安装到任意目录
- ✅ 可以从任何目录使用
- ✅ 不受限于原始项目位置
- ✅ 支持多环境部署

### 5. 打包优化
- 更新 `pyproject.toml` 配置
- 更新 `MANIFEST.in` 包含规则
- 使用 hatchling 构建系统
- 生成独立的 wheel 包

## 版本历史

- **v0.1.0** - 初始版本，支持基础 JLink 操作
- **v0.1.0 (重构)** - 支持独立部署，优化打包结构