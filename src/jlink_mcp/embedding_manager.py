"""Embedding Manager Module / 嵌入管理器模块.

This module manages OpenAI API embedding generation and caching.
此模块管理 OpenAI API 嵌入生成和缓存。

Features / 功能：
- Generate text embeddings using OpenAI API / 使用 OpenAI API 生成文本嵌入
- Cache embeddings using Pickle for fast startup / 使用 Pickle 缓存嵌入以实现快速启动
- Batch embedding generation for efficiency / 批量生成嵌入以提高效率
- Singleton pattern for global access / 单例模式以实现全局访问
"""

import hashlib
import os
import pickle
import tempfile
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore

from .utils import logger
from .config_manager import config_manager


class EmbeddingManager:
    """Embedding Manager (Singleton Pattern) / 嵌入管理器（单例模式）.

    Responsibilities / 职责：
    1. Generate text embeddings using OpenAI API / 使用 OpenAI API 生成文本嵌入
    2. Cache embeddings using Pickle / 使用 Pickle 缓存嵌入
    3. Batch optimization for API calls / API 调用的批量优化

    Design Pattern / 设计模式：
    - Singleton: Ensure only one instance exists / 单例：确保只存在一个实例
    - Lazy Initialization: Initialize OpenAI client on first use / 延迟初始化：首次使用时初始化 OpenAI 客户端
    - Cache First: Prioritize cached embeddings / 缓存优先：优先使用缓存的嵌入
    """

    _instance: Optional["EmbeddingManager"] = None
    _initialized: bool = False
    CACHE_VERSION: int = 1

    def __new__(cls) -> "EmbeddingManager":
        """Singleton pattern implementation / 单例模式实现."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize embedding manager / 初始化嵌入管理器."""
        if EmbeddingManager._initialized:
            return

        self._client: Optional[OpenAI] = None
        self._embedding_cache: Dict[str, List[float]] = {}
        self._cache_file: Path = self._get_cache_path()
        self._api_key: Optional[str] = None

        # Load cache from disk
        self._load_cache()

        EmbeddingManager._initialized = True
        logger.info("EmbeddingManager initialized")

    def _get_cache_path(self) -> Path:
        """Get cache file path / 获取缓存文件路径."""
        base_dir = (
            os.environ.get("JLINK_MCP_CACHE_DIR")
            or os.environ.get("LOCALAPPDATA")
            or os.environ.get("XDG_CACHE_HOME")
        )

        if not base_dir:
            if os.name == "nt":
                base_dir = str(Path.home() / "AppData" / "Local")
            else:
                base_dir = str(Path.home() / ".cache")

        cache_dir = Path(base_dir) / "jlink_mcp"

        try:
            cache_dir.mkdir(parents=True, exist_ok=True)
        except OSError:
            cache_dir = Path(tempfile.gettempdir()) / "jlink_mcp"
            cache_dir.mkdir(parents=True, exist_ok=True)

        return cache_dir / f"embeddings_v{self.CACHE_VERSION}.pkl"

    def _is_cache_enabled(self) -> bool:
        """Check whether cache is enabled / 检查是否启用缓存."""
        config = config_manager.get_config()
        return bool(getattr(config, "semantic_cache_enabled", True))

    def _load_cache(self) -> None:
        """Load embeddings from Pickle cache / 从 Pickle 缓存加载嵌入."""
        if not self._is_cache_enabled():
            logger.debug("Embedding cache disabled, skipping cache load")
            return

        if not self._cache_file.exists():
            logger.debug("Embedding cache file not found, starting with empty cache")
            return

        try:
            with open(self._cache_file, 'rb') as f:
                data = pickle.load(f)

                # Check cache version
                if data.get('version') != self.CACHE_VERSION:
                    logger.warning(f"Cache version mismatch, clearing cache (expected: {self.CACHE_VERSION}, got: {data.get('version')})")
                    return

                self._embedding_cache = data.get('cache', {})
                logger.info(f"Loaded {len(self._embedding_cache)} embeddings from cache")

        except Exception as e:
            logger.warning(f"Failed to load embedding cache: {e}")

    def _save_cache(self) -> None:
        """Save embeddings to Pickle cache / 保存嵌入到 Pickle 缓存."""
        if not self._is_cache_enabled():
            return

        try:
            data = {
                'version': self.CACHE_VERSION,
                'cache': self._embedding_cache,
                'timestamp': time.time(),
                'count': len(self._embedding_cache)
            }

            with open(self._cache_file, 'wb') as f:
                pickle.dump(data, f)

            logger.debug(f"Saved {len(self._embedding_cache)} embeddings to cache")

        except Exception as e:
            logger.warning(f"Failed to save embedding cache: {e}")

    def _get_api_key(self) -> str:
        """Get OpenAI/OpenRouter API Key / 获取 OpenAI/OpenRouter API Key.

        Priority / 优先级：
        1. Config file / 配置文件
        2. Environment variable OPENAI_API_KEY or OPENROUTER_API_KEY / 环境变量 OPENAI_API_KEY 或 OPENROUTER_API_KEY
        """
        if self._api_key:
            return self._api_key

        # Check config
        config = config_manager.get_config()
        if hasattr(config, 'semantic_api_key') and config.semantic_api_key:
            self._api_key = config.semantic_api_key
            return self._api_key

        # Check environment variables
        import os
        if "OPENAI_API_KEY" in os.environ:
            self._api_key = os.environ["OPENAI_API_KEY"]
            return self._api_key
        
        if "OPENROUTER_API_KEY" in os.environ:
            self._api_key = os.environ["OPENROUTER_API_KEY"]
            return self._api_key

        raise ValueError(
            "OpenAI/OpenRouter API Key not set. Please set it via one of the following methods:\n"
            "OpenAI/OpenRouter API Key 未设置。请通过以下方式之一设置：\n"
            "1. Config file: config.semantic_api_key / 配置文件：config.semantic_api_key\n"
            "2. Environment variable: OPENAI_API_KEY or OPENROUTER_API_KEY / 环境变量：OPENAI_API_KEY 或 OPENROUTER_API_KEY"
        )

    def _get_base_url(self) -> str:
        """Get base URL for API / 获取 API 的 base URL.

        Returns / 返回：
            str: Base URL (defaults to OpenAI, can be overridden to OpenRouter) / Base URL（默认为 OpenAI，可覆盖为 OpenRouter）
        """
        import os
        
        # Check for OpenRouter in environment
        if "OPENROUTER_API_KEY" in os.environ:
            return "https://openrouter.ai/api/v1"
        
        # Check config
        config = config_manager.get_config()
        if hasattr(config, 'semantic_base_url') and config.semantic_base_url:
            return config.semantic_base_url
        
        # Default to OpenAI
        return "https://api.openai.com/v1"

    def _initialize_client(self) -> None:
        """Initialize OpenAI/OpenRouter client (lazy initialization) / 初始化 OpenAI/OpenRouter 客户端（延迟初始化）."""
        if OpenAI is None:
            raise ImportError(
                "OpenAI library not installed. Please install it with: pip install openai>=1.0.0\n"
                "OpenAI 库未安装。请使用以下命令安装：pip install openai>=1.0.0"
            )

        if self._client is None:
            api_key = self._get_api_key()
            base_url = self._get_base_url()
            
            self._client = OpenAI(api_key=api_key, base_url=base_url)
            
            # Determine if using OpenRouter
            if "openrouter" in base_url.lower():
                logger.info(f"OpenRouter client initialized (base_url: {base_url})")
            else:
                logger.info("OpenAI client initialized")

    def get_embedding(self, text: str) -> List[float]:
        """Get text embedding with caching / 获取文本嵌入（带缓存）.

        Args / 参数：
            text: Text to generate embedding for / 要生成嵌入的文本

        Returns / 返回：
            List[float]: 1536-dimensional embedding vector / 1536 维嵌入向量

        Raises / 异常：
            ValueError: If OpenAI API Key is not set / 如果未设置 OpenAI API Key
            ImportError: If OpenAI library is not installed / 如果未安装 OpenAI 库
        """
        # Generate cache key
        cache_key = hashlib.md5(text.encode()).hexdigest()

        # Check cache
        if self._is_cache_enabled() and cache_key in self._embedding_cache:
            logger.debug(f"Embedding cache hit for text hash: {cache_key[:8]}...")
            return self._embedding_cache[cache_key]

        # Generate embedding
        logger.debug(f"Generating embedding for text hash: {cache_key[:8]}...")
        self._initialize_client()

        # Get model from config
        config = config_manager.get_config()
        model = getattr(config, 'semantic_embedding_model', 'text-embedding-ada-002')

        try:
            response = self._client.embeddings.create(  # type: ignore
                model=model,
                input=text
            )

            embedding = response.data[0].embedding

            # Cache the result
            if self._is_cache_enabled():
                self._embedding_cache[cache_key] = embedding
                self._save_cache()

            logger.debug(f"Generated embedding: {len(embedding)} dimensions")
            return embedding

        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise

    def get_batch_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts (batch optimization) / 获取多个文本的嵌入（批量优化）.

        Args / 参数：
            texts: List of texts to generate embeddings for / 要生成嵌入的文本列表

        Returns / 返回：
            List[List[float]]: List of 1536-dimensional embedding vectors / 1536 维嵌入向量列表
        """
        # Separate cached and uncached texts
        uncached_texts: List[str] = []
        uncached_indices: List[int] = []
        cache_keys: List[str] = []

        for i, text in enumerate(texts):
            cache_key = hashlib.md5(text.encode()).hexdigest()
            cache_keys.append(cache_key)

            if not self._is_cache_enabled() or cache_key not in self._embedding_cache:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Generate embeddings for uncached texts
        if uncached_texts:
            logger.info(f"Generating embeddings for {len(uncached_texts)} texts...")
            self._initialize_client()

            # Get model from config
            config = config_manager.get_config()
            model = getattr(config, 'semantic_embedding_model', 'text-embedding-ada-002')

            try:
                # Batch API call
                response = self._client.embeddings.create(  # type: ignore
                    model=model,
                    input=uncached_texts
                )

                # Cache new embeddings
                for i, emb in enumerate(response.data):
                    cache_key = hashlib.md5(uncached_texts[i].encode()).hexdigest()
                    if self._is_cache_enabled():
                        self._embedding_cache[cache_key] = emb.embedding

                if self._is_cache_enabled():
                    self._save_cache()

                if not self._is_cache_enabled():
                    return [emb.embedding for emb in response.data]

            except Exception as e:
                logger.error(f"Failed to generate batch embeddings: {e}")
                raise

        # Return all embeddings
        return [
            self._embedding_cache[cache_keys[i]]
            for i in range(len(texts))
        ]

    def clear_cache(self) -> None:
        """Clear embedding cache / 清除嵌入缓存."""
        self._embedding_cache.clear()

        if self._cache_file.exists():
            self._cache_file.unlink(missing_ok=True)

        logger.info("Embedding cache cleared")

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics / 获取缓存统计信息.

        Returns / 返回：
            Dict[str, Any]: Cache statistics including count, size, etc. / 缓存统计信息，包括数量、大小等
        """
        cache_size = self._cache_file.stat().st_size if self._cache_file.exists() else 0

        return {
            "count": len(self._embedding_cache),
            "size_bytes": cache_size,
            "size_mb": cache_size / (1024 * 1024),
            "cache_file": str(self._cache_file),
            "version": self.CACHE_VERSION
        }


# Global singleton instance / 全局单例实例
embedding_manager = EmbeddingManager()
