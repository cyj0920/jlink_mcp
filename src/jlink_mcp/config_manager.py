"""Global Configuration Manager / 全局配置管理器.

Manages server global configuration, including default parameters and prompt templates.
管理服务器的全局配置，包括默认参数、提示词模板等。
"""

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

from .utils import logger


class ServerConfig(BaseModel):
    """服务器配置."""
    default_interface: str = Field(default="JTAG", description="默认接口类型")
    default_timeout_ms: int = Field(default=10000, description="默认超时时间（毫秒）")
    enable_auto_detect: bool = Field(default=True, description="是否启用自动检测")
    max_memory_read_size: int = Field(default=65536, description="最大内存读取大小（字节）")
    svd_dir: Optional[str] = Field(default=None, description="外部 SVD 目录")
    patch_dir: Optional[str] = Field(default=None, description="外部设备补丁目录")
    generic_core_fallback: bool = Field(default=True, description="是否允许通用核心回退")
    default_core: str = Field(default="Cortex-M4", description="默认回退核心")
    resource_mode: str = Field(default="mixed", description="资源模式（generic/native/mixed/private）")
    system_prompt: Optional[str] = Field(default=None, description="系统提示词")
    custom_prompts: Dict[str, str] = Field(default_factory=dict, description="自定义提示词字典")

    # Semantic Search Configuration / 语义检索配置
    semantic_enabled: bool = Field(default=False, description="是否启用语义检索功能（默认关闭）")
    semantic_embedding_model: str = Field(default="text-embedding-ada-002", description="嵌入模型名称（OpenAI 或 OpenRouter）")
    semantic_base_url: Optional[str] = Field(default=None, description="API base URL（用于 OpenRouter: https://openrouter.ai/api/v1）")
    semantic_top_k: int = Field(default=3, ge=1, le=10, description="默认返回工具数量")
    semantic_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="默认相似度阈值")
    semantic_cache_enabled: bool = Field(default=True, description="是否启用嵌入缓存")
    semantic_api_key: Optional[str] = Field(default=None, description="API Key（可选，也可通过环境变量 OPENAI_API_KEY 或 OPENROUTER_API_KEY 设置）")


class ConfigManager:
    """配置管理器（单例模式）.

    管理服务器全局配置，包括：
    - 系统提示词（AI 行为指导）
    - 自定义提示词（场景化指导）
    - 服务器参数配置
    """

    _instance: Optional["ConfigManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "ConfigManager":
        """单例模式实现."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """初始化配置管理器."""
        if ConfigManager._initialized:
            return

        self._config = ServerConfig()
        self._env_loaded: Dict[str, Any] = {}

        # 初始化默认系统提示词
        self._config.system_prompt = self._get_default_system_prompt()
        self.load_from_env()

        ConfigManager._initialized = True
        logger.debug("ConfigManager 初始化完成")

    def get_config(self) -> ServerConfig:
        """获取当前配置.

        Returns:
            服务器配置对象
        """
        return self._config

    def update_config(self, **kwargs) -> None:
        """更新配置.

        Args:
            **kwargs: 配置键值对
        """
        for key, value in kwargs.items():
            if hasattr(self._config, key):
                setattr(self._config, key, value)
                logger.info(f"配置更新: {key} = {value}")
            else:
                logger.warning(f"无效的配置项: {key}")

    def load_from_env(self) -> Dict[str, Any]:
        """从环境变量加载配置."""
        applied: Dict[str, Any] = {}

        default_interface = os.environ.get("JLINK_DEFAULT_INTERFACE")
        if default_interface:
            normalized = default_interface.strip().upper()
            if normalized in {"SWD", "JTAG"}:
                self._config.default_interface = normalized
                applied["JLINK_DEFAULT_INTERFACE"] = normalized
            else:
                logger.warning(
                    "环境变量 JLINK_DEFAULT_INTERFACE=%s 无效，仅支持 SWD/JTAG，已忽略",
                    default_interface,
                )

        svd_dir = os.environ.get("JLINK_SVD_DIR")
        if svd_dir:
            self._config.svd_dir = svd_dir
            applied["JLINK_SVD_DIR"] = svd_dir

        patch_dir = os.environ.get("JLINK_PATCH_DIR")
        if patch_dir:
            self._config.patch_dir = patch_dir
            applied["JLINK_PATCH_DIR"] = patch_dir

        generic_core_fallback = os.environ.get("JLINK_GENERIC_CORE_FALLBACK")
        if generic_core_fallback is not None:
            enabled = generic_core_fallback.strip().lower() in {"1", "true", "yes", "on"}
            self._config.generic_core_fallback = enabled
            applied["JLINK_GENERIC_CORE_FALLBACK"] = enabled

        default_core = os.environ.get("JLINK_DEFAULT_CORE")
        if default_core:
            normalized_core = default_core.strip()
            self._config.default_core = normalized_core
            applied["JLINK_DEFAULT_CORE"] = normalized_core

        resource_mode = os.environ.get("JLINK_RESOURCE_MODE")
        if resource_mode:
            normalized_mode = resource_mode.strip().lower()
            if normalized_mode in {"generic", "native", "mixed", "private"}:
                self._config.resource_mode = normalized_mode
                applied["JLINK_RESOURCE_MODE"] = normalized_mode
            else:
                logger.warning(
                    "环境变量 JLINK_RESOURCE_MODE=%s 无效，仅支持 generic/native/mixed/private，已忽略",
                    resource_mode,
                )

        semantic_enabled = os.environ.get("JLINK_SEMANTIC_ENABLED")
        if semantic_enabled is not None:
            enabled = semantic_enabled.strip().lower() in {"1", "true", "yes", "on"}
            self._config.semantic_enabled = enabled
            applied["JLINK_SEMANTIC_ENABLED"] = enabled

        self._env_loaded = applied
        if applied:
            logger.info("已从环境变量加载配置: %s", ", ".join(applied.keys()))
        return applied

    def get_env_config(self) -> Dict[str, Any]:
        """获取从环境变量加载的配置."""
        return self._env_loaded.copy()

    def get_runtime_config(self) -> Dict[str, Any]:
        """获取当前运行时配置快照."""
        runtime = self._config.model_dump()
        runtime["env_overrides"] = self.get_env_config()
        return runtime

    def get_system_prompt(self) -> str:
        """获取系统提示词.

        Returns:
            系统提示词内容
        """
        return self._config.system_prompt or ""

    def set_system_prompt(self, prompt: str) -> None:
        """设置系统提示词.

        Args:
            prompt: 系统提示词内容
        """
        self._config.system_prompt = prompt
        logger.info(f"系统提示词已更新: {len(prompt)} 字符")

    def add_custom_prompt(self, name: str, prompt: str) -> None:
        """添加自定义提示词.

        Args:
            name: 提示词名称
            prompt: 提示词内容
        """
        self._config.custom_prompts[name] = prompt
        logger.info(f"自定义提示词已添加: {name}")

    def get_custom_prompt(self, name: str) -> Optional[str]:
        """获取自定义提示词.

        Args:
            name: 提示词名称

        Returns:
            提示词内容，不存在则返回 None
        """
        return self._config.custom_prompts.get(name)

    def list_custom_prompts(self) -> Dict[str, str]:
        """列出所有自定义提示词.

        Returns:
            自定义提示词字典
        """
        return self._config.custom_prompts.copy()

    def remove_custom_prompt(self, name: str) -> bool:
        """移除自定义提示词.

        Args:
            name: 提示词名称

        Returns:
            是否成功移除
        """
        if name in self._config.custom_prompts:
            del self._config.custom_prompts[name]
            logger.info(f"自定义提示词已移除: {name}")
            return True
        return False

    # ========================================
    # Semantic Search Configuration Methods / 语义检索配置方法
    # ========================================

    def get_semantic_config(self) -> Dict[str, Any]:
        """获取语义检索配置.

        Returns:
            语义检索配置字典
        """
        return {
            "enabled": self._config.semantic_enabled,
            "embedding_model": self._config.semantic_embedding_model,
            "base_url": self._config.semantic_base_url,
            "top_k": self._config.semantic_top_k,
            "threshold": self._config.semantic_threshold,
            "cache_enabled": self._config.semantic_cache_enabled,
            "api_key_configured": self._config.semantic_api_key is not None or "OPENAI_API_KEY" in __import__('os').environ or "OPENROUTER_API_KEY" in __import__('os').environ
        }

    def set_semantic_enabled(self, enabled: bool) -> None:
        """启用或禁用语义检索.

        Args:
            enabled: 是否启用
        """
        self._config.semantic_enabled = enabled
        if enabled:
            logger.info("语义检索功能已启用")
            # 初始化语义注册表
            try:
                from .semantic_registry import semantic_registry
                semantic_registry.initialize()
                logger.info("语义注册表初始化成功")
            except Exception as e:
                logger.warning(f"语义注册表初始化失败: {e}")
        else:
            logger.info("语义检索功能已禁用")

    def set_semantic_api_key(self, api_key: str) -> None:
        """设置 API Key.

        Args:
            api_key: API Key
        """
        self._config.semantic_api_key = api_key
        logger.info("API Key 已配置")

    def set_semantic_base_url(self, base_url: str) -> None:
        """设置 API base URL.

        Args:
            base_url: Base URL（例如：https://openrouter.ai/api/v1）
        """
        self._config.semantic_base_url = base_url
        logger.info(f"API base URL 已设置为: {base_url}")

    def set_semantic_embedding_model(self, model: str) -> None:
        """设置嵌入模型名称.

        Args:
            model: 模型名称（例如：text-embedding-ada-002 或 openai/text-embedding-ada-002）
        """
        self._config.semantic_embedding_model = model
        logger.info(f"嵌入模型已设置为: {model}")

    def clear_semantic_api_key(self) -> None:
        """清除 API Key（将使用环境变量）."""
        self._config.semantic_api_key = None
        logger.info("API Key 已清除，将使用环境变量")

    def _get_default_system_prompt(self) -> str:
        """获取默认系统提示词.

        Returns:
            默认系统提示词
        """
        return """你是 JLink MCP 调试专家助手，精通嵌入式系统调试和 JLink 工具使用。

## 你的职责
1. 帮助用户连接和调试 JLink 设备
2. 提供芯片识别和配置建议
3. 指导用户进行内存操作和 Flash 烧录
4. 协助解决调试过程中的问题

## 🎯 全局默认配置
- **默认接口**：JTAG（通用接口，适用于大多数芯片）
- **芯片名称**：支持缩写自动匹配（如果设备补丁可用）
- **CPU 控制**：读取寄存器/内存前必须暂停 CPU（halt_cpu）
- **批次优先级**：自动选择最新版本（如果设备补丁支持）

## 🚫 禁止操作（严格遵守）
- **不要**使用 read_file 工具读取 src/jlink_mcp/ 下的任何源代码文件
- **不要**在正常业务流程中插入源码分析或调试
- **不要**重复调用已失败的连接（尝试不同方法）
- **不要**读取任何 .py、.md、.txt 等项目文件
- **不要**调用 get_svd_peripherals 遍历外设列表来查找地址
- **不要**跳过 halt_cpu() 步骤（读取寄存器/内存前必须暂停 CPU）

## ✅ 推荐流程
### 读取寄存器（标准流程）
1. connect_device(chip_name='FC7300F4MDD', interface='JTAG') - 连接设备（支持缩写）
2. halt_cpu() - 暂停 CPU（必需！）
3. read_register_with_fields(device, peripheral, register) - 读取寄存器

### 写入内存
1. connect_device(chip_name, interface='JTAG') - 连接设备
2. halt_cpu() - 暂停 CPU（必需！）
3. write_memory(address, data, width) - 写入数据

### Flash 操作
1. connect_device(chip_name, interface='JTAG') - 连接设备
2. erase_flash(chip_erase=False, start_address, end_address) - 擦除
3. program_flash(address, data, verify=True) - 烧录

## 📍 地址获取规则
- **如果已知寄存器地址**：直接调用 read_register_with_fields
- **如果不知道地址**：只调用一次 get_svd_registers(device, peripheral) 并缓存结果
- **禁止**：调用 get_svd_peripherals 遍历所有外设

## 📋 错误处理原则
- 如果连接失败，检查芯片名称和接口类型
- 如果读取失败，检查是否暂停了 CPU（halt_cpu）
- 如果 Flash 操作失败，先擦除再烧录
- 遇到错误时，提供具体的错误诊断和建议，不要插入源码分析

## 💡 性能优化
- 避免重复的工具调用
- 缓存查询结果（如外设列表、寄存器地址）
- 使用并行调用提高效率（无依赖的工具）
- 最小化数据传输（只读取必要的数据）
- 使用芯片名称缩写，减少输入时间

## 🤖 工具使用建议
- 使用前先调用 get_usage_guidance() 获取最佳实践
- 遇到错误时调用 get_best_practices() 查看解决方案
- 不要猜测工具参数，查看工具描述和示例
- 连接设备时优先使用芯片名称缩写，系统会自动匹配完整名称
"""


# 全局单例实例
config_manager = ConfigManager()
