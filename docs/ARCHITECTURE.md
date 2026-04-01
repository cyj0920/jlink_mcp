# JLink MCP 架构设计文档

## 当前架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         用户层 (User Layer)                      │
│  AI Assistant / iFlow CLI / Command Line                        │
└────────────────────────────┬────────────────────────────────────┘
                             │ 调用 MCP 工具
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    MCP 协议层 (Protocol Layer)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  FastMCP Server (server.py)                             │  │
│  │  - 46个工具函数 (@mcp.tool() 装饰器)                     │  │
│  │  - 异步接口定义                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │ 调用工具函数
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                     工具层 (Tools Layer)                          │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │ connection.py │ │ device_info  │ │   memory.py  │             │
│  │ (5个工具)     │ │ (4个工具)    │ │ (4个工具)    │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │   flash.py   │ │   debug.py   │ │    rtt.py    │             │
│  │ (3个工具)    │ │ (7个工具)    │ │ (5个工具)    │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────────┐          │
│  │    svd.py    │ │  guidance.py │ │ configuration.py │          │
│  │ (5个工具)    │ │ (5个工具)    │ │ (3个工具)        │          │
│  └──────────────┘ └──────────────┘ └──────────────────┘          │
└────────────────────────────┬────────────────────────────────────┘
                             │ 调用管理器
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    管理层 (Manager Layer)                         │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │JLinkManager  │ │ SVDManager   │ │PatchManager  │             │
│  │(连接控制)    │ │(SVD解析)     │ │(设备补丁)    │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
│  ┌──────────────┐ ┌──────────────┐                               │
│  │ConfigManager │ │  GDBServer   │                               │
│  │(配置管理)    │ │(GDB服务)     │                               │
│  └──────────────┘ └──────────────┘                               │
└────────────────────────────┬────────────────────────────────────┘
                             │ 调用底层库
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    硬件抽象层 (HAL Layer)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  pylink-square (第三方库)                                │  │
│  │  - JLink SDK Python 封装                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    物理层 (Physical Layer)                        │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐             │
│  │  J-Link 硬件 │ │  目标芯片    │ │  电脑主机    │             │
│  └──────────────┘ └──────────────┘ └──────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

---

## 架构特点

### 优点：
1. **分层清晰**：从用户层到物理层，职责明确
2. **单例模式**：JLinkManager、SVDManager 等使用单例，确保资源唯一
3. **插件化设计**：通过 DevicePatchInterface 支持多厂商设备
4. **异步支持**：MCP 工具函数都是异步的
5. **类型安全**：使用 Pydantic 模型确保数据类型正确

### 局限性：
1. **单连接限制**：同一时间只能连接一个 JLink 设备
2. **平台依赖**：依赖 JLink DLL，需要安装 JLink 驱动
3. **线程安全**：部分操作非线程安全，需串行调用

---

## 性能指标

基于 J-Link V11 + FC7300 芯片的测试数据：

| 操作 | 典型耗时 | 说明 |
|------|---------|------|
| 设备枚举 | < 100ms | `list_jlink_devices()` |
| 设备连接 | 200-500ms | `connect_device()` |
| 内存读取 (1KB) | 5-10ms | `read_memory()` |
| 内存写入 (1KB) | 10-20ms | `write_memory()` |
| Flash 擦除 (64KB) | 1-3s | `erase_flash()` |
| Flash 烧录 (64KB) | 2-5s | `program_flash()` |
| SVD 加载 (首次) | 100-500ms | 依赖文件大小 |
| SVD 加载 (缓存) | < 10ms | 从 pickle 缓存读取 |

### 性能优化建议：
- 使用 SVD 缓存避免重复解析
- 批量内存操作优于多次小操作
- Flash 操作前先擦除再烧录

---

## 工具分类

| 分类 | 数量 | 主要功能 |
|------|------|---------|
| 连接管理 | 5 | 设备枚举、连接、断开、状态查询 |
| 设备信息 | 4 | 芯片信息、电压、扫描、补丁列表 |
| 内存操作 | 4 | 内存读写、寄存器读写 |
| Flash操作 | 3 | 擦除、烧录、校验 |
| 调试控制 | 7 | 复位、暂停、运行、单步、断点 |
| RTT | 5 | 启动、停止、读写、状态 |
| GDB Server | 3 | 启动、停止、状态 |
| SVD | 5 | 设备列表、外设、寄存器、解析 |
| 使用指南 | 5 | 指南、最佳实践、场景、禁止操作 |
| 配置诊断 | 3 | 运行时配置、能力探测、环境诊断 |

**总计：46 个工具**

---

## 数据模型层

```
models/
├── base.py      # MCPResponse, MCPError, OperationStatus
├── device.py    # DeviceInfo, ConnectionStatus, TargetInterface
├── operations.py # MemoryReadRequest, FlashProgramRequest, etc.
└── svd.py       # DeviceSVD, Peripheral, Register, Field
```

---

## 插件系统

```
plugins/
├── __init__.py
└── flagchip_patch.py  # Flagchip 设备补丁

device_patch_interface.py  # 插件接口定义
device_patch_manager.py    # 插件管理器
```

### 插件接口

```python
class DevicePatchInterface:
    @property
    def vendor_name(self) -> str
    
    @property
    def patch_version(self) -> str
    
    @property
    def device_names(self) -> list[str]
    
    @property
    def devices(self) -> list[dict]
    
    def is_available(self) -> bool
    
    def match_device_name(self, chip_name: str) -> str | None
    
    def find_similar_devices(self, partial_name: str, limit: int) -> list[str]
    
    def get_device_name_suggestions(self, partial_name: str) -> str
    
    def get_device_info(self, device_name: str) -> dict | None
    
    def supports_device(self, device_name: str) -> bool
```

#### 接口方法说明

| 方法 | 说明 |
|------|------|
| `vendor_name` | 厂商名称（如 Flagchip） |
| `patch_version` | 补丁版本号（如 v2.45） |
| `device_names` | 支持的设备名称列表 |
| `devices` | 设备详细信息列表 |
| `is_available()` | 检查补丁是否可用 |
| `match_device_name()` | 智能匹配设备名称 |
| `find_similar_devices()` | 查找相似设备名称 |
| `get_device_name_suggestions()` | 获取设备名称建议 |
| `get_device_info()` | 获取设备详细信息 |
| `supports_device()` | 检查是否支持设备 |

---

## 资源文件

```
resources/
└── JLink_Patch_v2.45/
    └── Devices/
        └── Flagchip/
            └── FC7300/
                ├── FC7300F8MDQxXxxxT1B_DFlash_FlexCore.elf
                ├── FC7300F8MDQxXxxxT1B_NVR_FlexCore.elf
                └── FC7300F8MDQxXxxxT1B_PFlash_FlexCore.elf

.svd_cache/  # SVD 解析缓存 (Pickle 格式)
```

---

## 配置管理

支持环境变量配置：

| 环境变量 | 说明 |
|---------|------|
| `JLINK_SVD_DIR` | 外部 SVD 目录 |
| `JLINK_PATCH_DIR` | 外部设备补丁目录 |
| `JLINK_DEFAULT_INTERFACE` | 默认接口类型 (SWD/JTAG) |
| `JLINK_GENERIC_CORE_FALLBACK` | 是否允许回退到通用 Cortex 核心调试 |
| `JLINK_DEFAULT_CORE` | 默认通用核心名称，如 `Cortex-M4` |
| `JLINK_RESOURCE_MODE` | 资源模式配置：`generic/native/mixed/private` |

---

## 错误处理架构

### 错误代码分类

| 范围 | 分类 | 说明 |
|------|------|------|
| 1-99 | 通用错误 | 未知错误、未初始化、已连接、参数无效 |
| 100-199 | 连接错误 | 设备未找到、连接失败、连接断开、目标未连接 |
| 200-299 | 操作错误 | 读/写/擦除/校验失败、操作超时 |
| 300-399 | 调试错误 | 目标运行中、目标已暂停、复位失败 |
| 400-499 | RTT 错误 | RTT 未启动、已启动、缓冲区未找到 |
| 500-599 | GDB Server 错误 | 启动失败、未运行、已运行 |

### 错误处理流程

```
┌─────────────────┐
│   工具调用      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐     成功      ┌─────────────────┐
│   执行操作      │─────────────→│   返回结果      │
└────────┬────────┘              └─────────────────┘
         │ 失败
         ↓
┌─────────────────┐
│ JLinkMCPError   │
│ (异常捕获)      │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 错误码映射      │
│ JLinkErrorCode  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ 返回标准格式    │
│ {               │
│   success: false│
│   error: {...}  │
│ }               │
└─────────────────┘
```

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": 101,
    "description": "连接失败",
    "detail": "设备未响应",
    "suggestion": "请检查设备连接状态，尝试重新插拔设备",
    "original_error": "JLink DLL error"
  }
}
```

---

## 典型工作流程

### 固件烧录流程

```
┌─────────────────┐
│ list_jlink_     │  检查设备连接
│ devices         │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ connect_device  │  连接目标芯片
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ get_target_info │  确认芯片信息
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ erase_flash     │  擦除 Flash
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ program_flash   │  烧录固件
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ verify_flash    │  校验固件
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ reset_target    │  复位运行
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ disconnect_     │  断开连接
│ device          │
└─────────────────┘
```

### 调试分析流程

```
┌─────────────────┐
│ connect_device  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ reset_target    │  复位后暂停
│ (halt)          │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ set_breakpoint  │  设置断点
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ run_cpu         │  运行到断点
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ read_registers  │  检查寄存器
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ read_memory     │  检查内存
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│ step_instruction│  单步调试
└─────────────────┘
```

---

## 扩展指南

### 添加新工具

1. 在 `src/jlink_mcp/tools/` 创建或编辑模块
2. 实现工具函数：
```python
@mcp.tool()
async def my_new_tool(param: str) -> dict:
    """工具描述"""
    return {"success": True, "data": result}
```
3. 在 `server.py` 中导入
4. 添加单元测试

### 添加新设备支持

1. 创建插件：`src/jlink_mcp/plugins/vendor_patch.py`
2. 实现接口：
```python
class VendorPatch(DevicePatchInterface):
    @property
    def vendor_name(self) -> str:
        return "VendorName"

    @property
    def device_names(self) -> list[str]:
        return ["DEVICE001", "DEVICE002"]
```
3. 注册插件到 `device_patch_manager.py`
4. 添加 ELF 文件到 `resources/`

### 添加新 SVD 支持

1. 获取 SVD 文件
2. 放置到 `.svd_cache/` 目录
3. SVDManager 自动加载

### 添加新模型

1. 在 `src/jlink_mcp/models/` 创建或编辑
2. 继承 `BaseModel`：
```python
from pydantic import BaseModel

class MyModel(BaseModel):
    field1: str
    field2: int = 0
```

---

## 参考资料

- [JLink SDK 文档](https://www.segger.com/products/debug-probes/j-link/tools/j-link-sdk/)
- [MCP 协议规范](https://modelcontextprotocol.io/)
- [Pydantic 文档](https://docs.pydantic.dev/)


