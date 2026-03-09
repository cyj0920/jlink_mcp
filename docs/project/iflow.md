# JLink MCP 项目

## 项目概述

这是一个 MCP (Model Context Protocol) 服务器项目，旨在为 AI 提供与 JLink 调试器交互的能力，打通 AI 与硬件 MCU 芯片之间的桥梁。

## 核心功能

- **芯片识别**: 读取芯片ID、Flash大小、设备型号
- **内存操作**: 读写 RAM/Flash、查看寄存器
- **调试控制**: 复位、运行、暂停、单步执行
- **固件操作**: 下载程序、擦除 Flash、校验
- **日志输出**: RTT（实时传输）读取调试日志

## 技术栈

- **语言**: Python 3.12+
- **核心库**: pylink-square (JLink Python 封装)
- **协议**: MCP (Model Context Protocol)
- **架构**: MCP Server -> JLink SDK -> JLink 调试器 -> 目标 MCU

## 项目结构

```
jlink_mcp/
├── .iflow/              # iFlow CLI 配置
│   └── settings.json    # 项目配置
├── src/
│   └── jlink_mcp/       # 主代码目录
│       ├── __init__.py
│       ├── server.py    # MCP 服务器主文件
│       └── jlink_wrapper.py  # JLink 封装
├── tests/               # 测试目录
├── pyproject.toml       # Python 项目配置
├── README.md           # 项目说明
└── IFLOW.md            # 本文件 (AI 上下文)
```

## 开发规范

### 代码风格
- 使用 4 空格缩进
- 遵循 PEP 8 规范
- 函数和类添加清晰的 docstring
- 类型注解是必需的

### 命名规范
- 类名: PascalCase (如 `JLinkManager`)
- 函数/变量: snake_case (如 `connect_device`)
- 常量: UPPER_SNAKE_CASE
- 私有成员: 以下划线为前缀 `_`

### 错误处理
- 所有 JLink 操作必须包装 try-except
- 提供清晰的错误信息
- 记录详细的调试日志

### 安全注意
- 不要硬编码敏感信息（如 API 密钥）
- 使用环境变量存储配置
- 对文件操作进行权限检查

## MCP 工具设计

每个工具应该：
1. 有清晰的名称和描述
2. 定义明确的输入参数
3. 返回结构化的结果
4. 包含错误处理

## 依赖项

主要依赖：
- `pylink-square`: JLink Python 接口
- `mcp`: MCP 协议实现
- `pydantic`: 数据验证

## 参考资料

- [pylink-square 文档](https://pylink.readthedocs.io/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [SEGGER JLink 文档](https://www.segger.com/downloads/jlink/)
