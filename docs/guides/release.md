# JLink MCP 发布指南

## 快速开始（用户角度）

### 安装（使用 UV - 推荐）

[UV](https://github.com/astral-sh/uv) 是一个极速 Python 包管理器，比 pip 快 10-100 倍。

```bash
# 1. 安装 uv
pip install uv

# 2. 创建虚拟环境
uv venv --python 3.12

# 3. 激活环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. 安装 jlink-mcp
uv pip install jlink-mcp

# 或从源码安装
git clone https://github.com/your-repo/jlink-mcp.git
cd jlink-mcp
uv pip install -e .
```

### 安装（传统 pip 方式）

```bash
# 从 PyPI 安装
pip install jlink-mcp

# 或从源码安装
git clone https://github.com/your-repo/jlink-mcp.git
cd jlink-mcp
pip install -e .
```

### 使用

```bash
# 启动 MCP 服务器
jlink-mcp

# 或在 iFlow CLI 中自动使用
iflow
```

---

## 发布步骤（维护者角度）

### 1. 准备工作

**安装发布工具**:
```bash
pip install build twine
```

**检查项目**:
```bash
# 运行测试
python -m pytest

# 检查代码格式
black src/
ruff check src/

# 检查类型
mypy src/jlink_mcp
```

### 2. 更新版本号

编辑 `pyproject.toml`:
```toml
[project]
version = "0.1.1"  # 更新版本号
```

### 3. 构建分发包

```bash
# 清理旧构建
rm -rf dist/ build/ *.egg-info

# 构建
python -m build

# 检查构建结果
twine check dist/*
```

### 4. 测试安装

```bash
# 创建虚拟环境测试
python -m venv test_env
test_env\Scripts\activate  # Windows
test_env/bin/activate      # Linux/Mac

# 安装测试
pip install dist/jlink_mcp-0.1.1-py3-none-any.whl

# 验证安装
jlink-mcp --help
```

### 5. 发布到 PyPI

**测试发布（TestPyPI）**:
```bash
twine upload --repository testpypi dist/*

# 测试安装
git check-ignorepip install --index-url https://test.pypi.org/simple/ jlink-mcp
```

**正式发布（PyPI）**:
```bash
twine upload dist/*
```

需要输入 PyPI 账号和密码（或 API Token）。

### 6. 创建 Git Tag

```bash
# 提交所有更改
git add .
git commit -m "Release v0.1.1"

# 创建标签
git tag -a v0.1.1 -m "Release version 0.1.1"

# 推送标签
git push origin v0.1.1
```

### 7. 创建 GitHub Release

1. 打开 GitHub 仓库页面
2. 点击 "Releases" → "Create a new release"
3. 选择标签 `v0.1.1`
4. 填写发布说明
5. 上传 `dist/` 中的文件作为附件

---

## 发布检查清单

### 发布前检查

- [ ] 所有测试通过
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] 文档已更新
- [ ] 代码已格式化（black, ruff）
- [ ] 类型检查通过（mypy）

### 发布内容

- [ ] 源码分发包（.tar.gz）
- [ ]  Wheel 分发包（.whl）
- [ ] Git Tag 已创建
- [ ] GitHub Release 已发布
- [ ] PyPI 包已上传

---

## 用户使用指南

### 方式 1: pip 安装（推荐）

```bash
pip install jlink-mcp
```

### 方式 2: 源码安装

```bash
git clone https://github.com/your-repo/jlink-mcp.git
cd jlink-mcp
pip install -e .
```

### 方式 3: Docker

```bash
# 构建镜像
docker build -t jlink-mcp .

# 运行
docker run -it --rm jlink-mcp
```

---

## 在 iFlow CLI 中使用

### 配置 iFlow

编辑 `.iflow/settings.json`:

```json
{
  "mcpServers": {
    "jlinkMcpServer": {
      "command": "jlink-mcp",
      "timeout": 30000
    }
  }
}
```

### 启动 iFlow

```bash
iflow
```

然后 AI 就可以调用 JLink MCP 工具了！

---

## 常见问题

### Q: 发布到 PyPI 需要什么？

A: 需要：
1. PyPI 账号（在 https://pypi.org 注册）
2. API Token（推荐）或用户名密码
3. 在 `~/.pypirc` 中配置：

```ini
[pypi]
username = __token__
password = pypi-xxxxxxxxxx
```

### Q: 如何更新已发布的包？

A: 修改版本号（如 0.1.0 → 0.1.1），重新构建并上传。PyPI 不允许重复上传同一版本。

### Q: 构建失败怎么办？

A: 检查：
1. `pyproject.toml` 配置是否正确
2. 所有依赖是否都已安装
3. 源码是否在 `src/` 目录下

---

## 版本号规范

使用语义化版本（SemVer）：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的问题修复

示例：
- `0.1.0` - 初始版本
- `0.1.1` - 文档和发布流程更新
- `0.2.0` - 新功能
- `1.0.0` - 正式发布
