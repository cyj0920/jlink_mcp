# UV 使用指南

本项目使用 [uv](https://github.com/astral-sh/uv) 作为包管理器，比 pip 快 10-100 倍。

## 安装 UV

### 方式 1: 使用 pip (推荐)

```bash
pip install uv
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

---

## 快速开始

### 1. 克隆项目

```bash
git clone https://github.com/cyj0920/jlink_mcp.git
cd jlink_mcp
```

### 2. 创建虚拟环境

```bash
uv venv --python 3.12

# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
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
jlink-mcp
# 或
python -c "import jlink_mcp; print('安装成功')"
```

---

## UV 常用命令

### 包管理

```bash
uv pip install <package>      # 安装包
uv pip install <package>==1.0.0  # 安装指定版本
uv pip uninstall <package>    # 卸载包
uv pip install --upgrade <package>  # 升级包
uv pip list                   # 查看已安装包
uv pip freeze > requirements.txt  # 导出依赖
```

### 虚拟环境

```bash
uv venv                       # 创建虚拟环境
uv venv --python 3.12         # 指定 Python 版本
uv venv --clear               # 删除并重建
```

---

## 与 pip 的对比

| 功能 | pip | uv |
|------|-----|-----|
| 安装速度 | 慢 | 极快 |
| 依赖解析 | 一般 | 精准 |
| 锁定文件 | 需 pip-tools | 内置 |
| 虚拟环境 | 需 venv | 内置 |
| 缓存 | 一般 | 极速缓存 |

---

## 项目开发工作流

### 日常开发

```bash
# 1. 激活环境
.venv\Scripts\activate

# 2. 安装依赖
uv pip install -e ".[dev]"

# 3. 运行测试
pytest

# 4. 运行 MCP 服务器
jlink-mcp
```

### 添加新依赖

```bash
# 编辑 pyproject.toml 中的 dependencies
uv pip install -e .
```

### 依赖管理最佳实践

#### 固定版本号

```toml
# pyproject.toml
dependencies = [
    "pylink-square>=0.5.0,<0.6.0",  # 限制主版本
    "pydantic>=2.0.0",
]
```

#### 开发依赖分离

```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
```

#### 导出依赖锁定

```bash
# 导出完整依赖
uv pip freeze > requirements.txt

# 仅导出项目依赖
uv pip freeze | grep -v "^\-e" > requirements.txt
```

### 常见开发命令

```bash
# 代码格式化
black src/

# 代码检查
ruff check src/

# 类型检查
mypy src/jlink_mcp

# 运行测试
pytest tests/ -v

# 测试覆盖率
pytest tests/ --cov=src/jlink_mcp --cov-report=html
```

---

## 故障排除

### Q: uv 命令找不到

**A**: 检查 PATH 或使用 `python -m uv --version`

### Q: 虚拟环境创建失败

**A**:
```bash
Remove-Item -Recurse -Force .venv
uv venv --python 3.12
```

### Q: 安装依赖失败

**A**:
```bash
uv cache clean
uv pip install -e . --no-cache
```

---

## 参考链接

- [UV 官方文档](https://docs.astral.sh/uv/)
- [UV GitHub](https://github.com/astral-sh/uv)