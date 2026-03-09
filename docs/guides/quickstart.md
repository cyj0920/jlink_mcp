# JLink MCP 快速开始

## 方式 1: 使用 UV (推荐 - 极速)

```bash
# 1. 安装 uv
pip install uv

# 2. 克隆项目
git clone <repo-url>
cd jlink-mcp

# 3. 创建虚拟环境
uv venv --python 3.12

# 4. 激活环境 (Windows)
.venv\Scripts\activate

# 5. 安装依赖
uv pip install -e .

# 6. 运行测试
python test_fc7300.py

# 7. 启动 MCP 服务器
jlink-mcp
```

## 方式 2: 使用传统 pip

```bash
# 1. 克隆项目
git clone <repo-url>
cd jlink-mcp

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活环境 (Windows)
.venv\Scripts\activate

# 4. 安装依赖
pip install -e .

# 5. 运行测试
python test_fc7300.py

# 6. 启动 MCP 服务器
jlink-mcp
```

## iFlow CLI 配置

编辑 `.iflow/settings.json`:

```json
{
  "mcpServers": {
    "jlinkMcpServer": {
      "command": ".venv\\Scripts\\python.exe",
      "args": ["-m", "jlink_mcp.server"],
      "timeout": 30000
    }
  }
}
```

然后启动 iFlow:
```bash
iflow
```

## 常用 UV 命令

```bash
# 安装包
uv pip install <package>

# 查看已安装
uv pip list

# 更新依赖
uv pip install -e . --upgrade

# 运行测试
uv run python test_fc7300.py

# 查看帮助
uv --help
```

## 项目结构

```
jlink_mcp/
├── src/jlink_mcp/          # 源代码
├── docs/                   # 文档
│   ├── guides/             # 使用指南
│   ├── project/            # 项目文档
│   └── reference/          # API 参考
├── tool/                   # 工具文件
│   ├── JLink_Patch_v2.45/  # Flagchip 补丁
│   └── SVD_V1.5.6/         # SVD 定义文件
├── test_fc7300.py          # 硬件测试
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

## 获取帮助

- 📖 [UV 使用指南](./uv-guide.md)
- 📚 [API 文档](../reference/api.md)
- 💡 [使用示例](../reference/examples.md)
- ❓ [常见问题](../reference/faq.md)
- 🚀 [发布指南](./release.md)

## 硬件验证

✅ **FC7300F4MDSXXXXXT1C** (Flagchip)
- 连接: J-Link V11 via JTAG
- 日期: 2026-02-10
- 通过: 连接、复位、寄存器读取

**当前版本**: v0.1.1 (已发布到 PyPI)

---

**提示**: 首次使用请确保 JLink 驱动已安装并连接硬件。
