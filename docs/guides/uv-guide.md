# UV 使用指南

本项目使用 [uv](https://github.com/astral-sh/uv) 作为包管理器，它是一个用 Rust 编写的极速 Python 包管理工具。

## 什么是 UV？

UV 是一个超快速的 Python 包管理器和环境管理工具：
- ⚡ **极速**: 比 pip 快 10-100 倍
- 🔒 **可靠**: 内置依赖锁定
- 🎯 **简单**: 兼容 pip 命令
- 📦 **统一**: 替代 pip + venv + pip-tools

## 安装 UV

### 方式 1: 使用 pip (推荐)
```bash
pip install uv
# 或
pip install --user uv
```

### 方式 2: 使用官方安装脚本
**Windows (PowerShell)**:
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-repo/jlink-mcp.git
cd jlink-mcp
```

### 2. 创建虚拟环境
```bash
# 使用 uv 创建虚拟环境
uv venv --python 3.12

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

### 3. 安装依赖
```bash
# 安装项目依赖（可编辑模式）
uv pip install -e .

# 安装开发依赖
uv pip install -e ".[dev]"
```

### 4. 验证安装
```bash
# 运行 MCP 服务器
jlink-mcp

# 或测试导入
python -c "import jlink_mcp; print('✅ 安装成功')"
```

## UV 常用命令

### 包管理
```bash
# 安装包
uv pip install <package>

# 安装指定版本
uv pip install <package>==1.0.0

# 卸载包
uv pip uninstall <package>

# 升级包
uv pip install --upgrade <package>

# 查看已安装包
uv pip list

# 导出依赖
uv pip freeze > requirements.txt
```

### 虚拟环境
```bash
# 创建虚拟环境
uv venv

# 指定 Python 版本
uv venv --python 3.12

# 使用特定解释器
uv venv --python python3.11

# 删除并重建
uv venv --clear
```

### 依赖锁定（高级）
```bash
# 生成锁定文件 (uv.lock)
uv lock

# 根据锁定文件安装
uv sync

# 更新锁定
uv lock --upgrade
```

## 与 pip 的对比

| 功能 | pip | uv |
|------|-----|-----|
| 安装速度 | 慢 | ⚡ 极快 |
| 依赖解析 | 一般 | 🎯 精准 |
| 锁定文件 | 需 pip-tools | ✅ 内置 |
| 虚拟环境 | 需 venv | ✅ 内置 |
| 缓存 | 一般 | 🚀 极速缓存 |
| 兼容性 | 标准 | ✅ 兼容 pip |

## 项目开发工作流

### 日常开发
```bash
# 1. 激活环境
.venv\Scripts\activate

# 2. 安装依赖（首次）
uv pip install -e ".[dev]"

# 3. 运行测试
python -m pytest

# 4. 格式化代码
black src/
ruff check src/

# 5. 运行 MCP 服务器
jlink-mcp
```

### 添加新依赖
```bash
# 编辑 pyproject.toml 中的 dependencies

# 然后安装
uv pip install -e .

# 更新锁定文件（如果使用 uv.lock）
uv lock
```

### 发布前准备
```bash
# 1. 清理环境
uv pip uninstall jlink-mcp

# 2. 重新安装验证
uv pip install -e .

# 3. 运行完整测试
python test_fc7300.py

# 4. 构建分发包
python -m build
```

## 故障排除

### Q: uv 命令找不到
**A**: 
```bash
# 确保 uv 在 PATH 中
which uv
# 或
python -m uv --version
```

### Q: 虚拟环境创建失败
**A**: 
```bash
# 删除旧环境后重建
rm -rf .venv
uv venv --python 3.12
```

### Q: 安装依赖失败
**A**:
```bash
# 清理缓存重试
uv cache clean
uv pip install -e . --no-cache
```

### Q: 权限问题
**A**:
```bash
# Windows - 以管理员身份运行 PowerShell
# Linux/Mac - 使用 --user 或虚拟环境
uv pip install --user uv
```

## 高级用法

### 使用 UV 运行脚本
```bash
# 无需激活环境，直接运行
uv run python test_fc7300.py

# 运行模块
uv run -m jlink_mcp.server
```

### 多 Python 版本管理
```bash
# 安装特定 Python 版本
uv python install 3.11 3.12

# 创建指定版本环境
uv venv --python 3.11

# 查看可用版本
uv python list
```

### 工作区（Workspace）
如果你有多个相关项目：
```bash
# 在项目根目录
uv sync --workspace
```

## 参考链接

- [UV 官方文档](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)
- [PyPI - uv](https://pypi.org/project/uv/)

---

**提示**: UV 完全兼容 pip，你可以随时切换回 pip 如果 needed。
