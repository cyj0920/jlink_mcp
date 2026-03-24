# JLink MCP 发布指南

## 安装（用户角度）

### 使用 UV (推荐)

```bash
# 安装 uv
pip install uv

# 创建虚拟环境
uv venv --python 3.12

# 激活环境
.venv\Scripts\activate  # Windows

# 安装 jlink-mcp
uv pip install jlink-mcp

# 或从源码安装
git clone https://github.com/cyj0920/jlink_mcp.git
cd jlink_mcp
uv pip install -e .
```

### 使用 pip

```bash
# 从 PyPI 安装
pip install jlink-mcp

# 或从源码安装
git clone https://github.com/cyj0920/jlink_mcp.git
cd jlink_mcp
pip install -e .
```

---

## 发布步骤（维护者角度）

### 1. 准备工作

```bash
pip install build twine
```

### 2. 检查项目

```bash
pytest tests/
black src/
ruff check src/
mypy src/jlink_mcp
```

### 3. 更新版本号

编辑 `pyproject.toml`:
```toml
[project]
version = "0.1.1"
```

### 4. 构建分发包

```bash
# 清理旧构建 (Windows)
Remove-Item -Recurse -Force dist, build, *.egg-info -ErrorAction SilentlyContinue

# 构建
python -m build

# 检查
twine check dist/*
```

### 5. 测试安装

```bash
python -m venv test_env
test_env\Scripts\activate
pip install dist/jlink_mcp-0.1.1-py3-none-any.whl
jlink-mcp --help
```

### 6. 发布到 PyPI

**测试发布（TestPyPI）**:
```bash
twine upload --repository testpypi dist/*
```

**正式发布（PyPI）**:
```bash
twine upload dist/*
```

### 7. 创建 Git Tag

```bash
git add .
git commit -m "Release v0.1.1"
git tag -a v0.1.1 -m "Release version 0.1.1"
git push origin v0.1.1
```

---

## 发布检查清单

### 发布前
- [ ] 所有测试通过
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] 代码已格式化

### 发布内容
- [ ] 源码分发包 (.tar.gz)
- [ ] Wheel 分发包 (.whl)
- [ ] Git Tag 已创建
- [ ] PyPI 包已上传

---

## 版本号规范

使用语义化版本：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的问题修复

示例：
- `0.1.0` - 初始版本
- `0.1.1` - 文档更新
- `0.2.0` - 新功能
- `1.0.0` - 正式发布

---

## CI/CD 自动化

项目使用 GitHub Actions 实现自动化发布。

### 自动发布流程

配置文件：`.github/workflows/python-publish.yml`

**触发条件**：
- 推送 tag（格式：`v*.*.*`）

**自动步骤**：
1. 检出代码
2. 设置 Python 环境
3. 安装依赖
4. 构建分发包
5. 发布到 PyPI

### 手动触发发布

```bash
# 1. 更新版本号
# 编辑 pyproject.toml 中的 version

# 2. 提交并打 tag
git add .
git commit -m "Release v0.1.2"
git tag v0.1.2
git push origin main --tags

# 3. GitHub Actions 自动执行发布
```

### GitHub Secrets 配置

需要在仓库设置中配置：

| Secret | 说明 |
|--------|------|
| `PYPI_API_TOKEN` | PyPI API Token |
| `TEST_PYPI_API_TOKEN` | TestPyPI API Token（可选） |

---

## 安全注意事项

### PyPI Token 管理

- 不要在代码中硬编码 Token
- 使用 GitHub Secrets 存储敏感信息
- 定期轮换 API Token

### 发布前检查

- [ ] 代码无敏感信息
- [ ] `.gitignore` 配置正确
- [ ] 依赖版本已锁定
- [ ] 无已知安全漏洞

### 版本号规范

使用语义化版本：`MAJOR.MINOR.PATCH`

- **MAJOR**: 不兼容的 API 变更
- **MINOR**: 向后兼容的功能添加
- **PATCH**: 向后兼容的问题修复

示例：
- `0.1.0` - 初始版本
- `0.1.1` - Bug 修复
- `0.2.0` - 新功能
- `1.0.0` - 正式稳定版

---

## 版本兼容性

| JLink MCP | Python | JLink SDK | pylink-square |
|-----------|--------|-----------|---------------|
| 0.1.x | 3.8+ | 7.0+ | 0.5.0+ |

### 升级指南

从 0.1.x 升级到 0.2.x：
- API 保持兼容
- 新增工具无需修改现有代码
- 检查 CHANGELOG.md 了解变更