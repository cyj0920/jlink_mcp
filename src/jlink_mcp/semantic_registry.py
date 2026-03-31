"""Semantic Tool Registry Module / 语义工具注册表模块.

This module manages tool metadata and provides semantic search functionality.
此模块管理工具元数据并提供语义搜索功能。

Based on the paper "Semantic Tool Discovery for Large Language Models: A Vector-Based Approach to MCP Tool Selection"
基于论文《Semantic Tool Discovery for Large Language Models: A Vector-Based Approach to MCP Tool Selection》

Features / 功能：
- Scan all MCP tools and extract metadata / 扫描所有 MCP 工具并提取元数据
- Build tool documents following paper template / 遵循论文模板构建工具文档
- Generate embeddings for all tools / 为所有工具生成嵌入
- Perform semantic search using cosine similarity / 使用余弦相似度执行语义搜索
- Singleton pattern for global access / 单例模式以实现全局访问
"""

import inspect
import numpy as np
from typing import Dict, List, Optional, Set, Any

from .models.semantic import (
    ToolEmbedding,
    SemanticSearchResult,
    SemanticRegistryConfig
)
from .embedding_manager import embedding_manager
from .utils import logger
from .tools.guidance import TOOL_CATEGORIES, USAGE_SCENARIOS


class SemanticRegistry:
    """Semantic Tool Registry (Singleton Pattern) / 语义工具注册表（单例模式）.

    Responsibilities / 职责：
    1. Scan all MCP tools and extract metadata / 扫描所有 MCP 工具并提取元数据
    2. Build tool documents following paper template / 遵循论文模板构建工具文档
    3. Generate embeddings for all tools / 为所有工具生成嵌入
    4. Perform semantic search (cosine similarity) / 执行语义搜索（余弦相似度）

    Design Pattern / 设计模式：
    - Singleton: Ensure only one instance exists / 单例：确保只存在一个实例
    - Lazy Initialization: Initialize on first search / 延迟初始化：首次搜索时初始化
    - Cache First: Use pre-computed embeddings / 缓存优先：使用预计算的嵌入

    Paper Template / 论文模板：
        Tool: {tool_name}
        Purpose: {description}
        Capabilities: {expanded_description}
        Parameters: {parameter_descriptions}
    """

    _instance: Optional["SemanticRegistry"] = None
    _initialized: bool = False

    def __new__(cls) -> "SemanticRegistry":
        """Singleton pattern implementation / 单例模式实现."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize semantic registry / 初始化语义注册表."""
        if SemanticRegistry._initialized:
            return

        self._tools: Dict[str, ToolEmbedding] = {}
        self._tool_embeddings_matrix: Optional[np.ndarray] = None
        self._tool_names_list: List[str] = []
        self._config: SemanticRegistryConfig = SemanticRegistryConfig()
        self._embedding_manager = embedding_manager

        SemanticRegistry._initialized = True
        logger.info("SemanticRegistry initialized")

    def initialize(self, force: bool = False) -> None:
        """Initialize registry: scan tools and generate embeddings / 初始化注册表：扫描工具并生成嵌入.

        Args / 参数：
            force: Force re-initialization even if already initialized / 强制重新初始化，即使已经初始化
        """
        if self._initialized and not force:
            logger.info("Registry already initialized, skipping")
            return

        logger.info("Initializing semantic registry...")

        # Scan all tools
        self._scan_tools()

        # Generate embeddings
        self._generate_embeddings()

        # Build embeddings matrix for efficient search
        self._build_embeddings_matrix()

        self._initialized = True
        logger.info(f"Semantic registry initialized with {len(self._tools)} tools")

    def _scan_tools(self) -> None:
        """Scan all MCP tools and extract metadata / 扫描所有 MCP 工具并提取元数据."""
        # Collect all tool names from categories
        all_tool_names: Set[str] = set()
        category_map: Dict[str, str] = {}  # tool_name -> category

        for category_name, category_info in TOOL_CATEGORIES.items():
            for tool_name in category_info["tools"]:
                all_tool_names.add(tool_name)
                category_map[tool_name] = category_name

        logger.info(f"Found {len(all_tool_names)} tools in {len(TOOL_CATEGORIES)} categories")

        # Build tool metadata for each tool
        for tool_name in all_tool_names:
            tool_emb = self._build_tool_metadata(tool_name, category_map[tool_name])
            self._tools[tool_name] = tool_emb

    def _build_tool_metadata(self, tool_name: str, category: str) -> ToolEmbedding:
        """Build tool metadata / 构建工具元数据.

        Args / 参数：
            tool_name: Tool name / 工具名称
            category: Tool category / 工具分类

        Returns / 返回：
            ToolEmbedding: Tool metadata with empty embedding / 带有空嵌入的工具元数据
        """
        # Extract docstring (will be retrieved from actual function in production)
        doc_string = self._get_tool_docstring(tool_name)

        # Build expanded description from usage scenarios
        expanded_description = self._build_expanded_description(tool_name)

        # Build parameter descriptions
        parameter_descriptions = self._build_parameter_descriptions(tool_name)

        return ToolEmbedding(
            tool_name=tool_name,
            tool_category=category,
            doc_string=doc_string,
            expanded_description=expanded_description,
            parameter_descriptions=parameter_descriptions,
            embedding_vector=[]  # Will be filled later
        )

    def _get_tool_docstring(self, tool_name: str) -> str:
        """Get tool docstring / 获取工具文档字符串.

        Args / 参数：
            tool_name: Tool name / 工具名称

        Returns / 返回：
            str: Tool docstring / 工具文档字符串
        """
        # In production, this would extract from actual function
        # For now, use a placeholder
        return f"Tool: {tool_name}"

    def _build_expanded_description(self, tool_name: str) -> str:
        """Build expanded description from usage scenarios / 从使用场景构建扩展描述.

        Args / 参数：
            tool_name: Tool name / 工具名称

        Returns / 返回：
            str: Expanded description / 扩展描述
        """
        descriptions: List[str] = []

        # Search for tool in usage scenarios
        for scenario_name, scenario_info in USAGE_SCENARIOS.items():
            steps_str = " ".join(scenario_info.get("steps", []))
            if tool_name in steps_str:
                descriptions.append(scenario_info["description"])

        if descriptions:
            return " ".join(descriptions)
        else:
            return f"Functionality for {tool_name}"

    def _build_parameter_descriptions(self, tool_name: str) -> str:
        """Build parameter descriptions / 构建参数描述.

        Args / 参数：
            tool_name: Tool name / 工具名称

        Returns / 返回：
            str: Parameter descriptions / 参数描述
        """
        # In production, this would extract from function signature
        # For now, use a placeholder
        return "Parameters vary by tool"

    def _generate_embeddings(self) -> None:
        """Generate embeddings for all tools / 为所有工具生成嵌入."""
        logger.info(f"Generating embeddings for {len(self._tools)} tools...")

        # Prepare texts for batch embedding
        texts = []
        tool_names = []

        for tool_name, tool_emb in self._tools.items():
            text = tool_emb.to_embedding_text()
            texts.append(text)
            tool_names.append(tool_name)

        # Generate embeddings in batch
        try:
            embeddings = self._embedding_manager.get_batch_embeddings(texts)

            # Update tool embeddings
            for tool_name, embedding in zip(tool_names, embeddings):
                self._tools[tool_name].embedding_vector = embedding

            logger.info(f"Generated embeddings for {len(embeddings)} tools")

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    def _build_embeddings_matrix(self) -> None:
        """Build embeddings matrix for efficient search / 构建嵌入矩阵以实现高效搜索."""
        if not self._tools:
            return

        self._tool_names_list = list(self._tools.keys())
        embeddings = [
            self._tools[name].embedding_vector
            for name in self._tool_names_list
        ]

        self._tool_embeddings_matrix = np.array(embeddings, dtype=np.float32)

        logger.info(f"Built embeddings matrix: {self._tool_embeddings_matrix.shape}")

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: float = 0.5
    ) -> List[SemanticSearchResult]:
        """Perform semantic search / 执行语义搜索.

        Args / 参数：
            query: User query in natural language / 用户自然语言查询
            top_k: Number of results to return / 返回结果数量
            threshold: Similarity threshold (0-1) / 相似度阈值（0-1）

        Returns / 返回：
            List[SemanticSearchResult]: Search results sorted by relevance / 按相关度排序的搜索结果
        """
        # Initialize if not already done
        if not self._initialized:
            self.initialize()

        # Generate query embedding
        logger.debug(f"Generating embedding for query: {query[:50]}...")
        query_embedding = self._embedding_manager.get_embedding(query)

        # Calculate cosine similarities
        similarities = self._cosine_similarity_batch(query_embedding)

        # Filter by threshold
        above_threshold = similarities >= threshold

        # Get top-k indices
        if np.any(above_threshold):
            # Only consider results above threshold
            valid_indices = np.where(above_threshold)[0]
            valid_similarities = similarities[valid_indices]

            # Sort by similarity (descending)
            top_indices = np.argsort(valid_similarities)[::-1][:top_k]

            # Map back to original indices
            final_indices = valid_indices[top_indices]
            final_scores = valid_similarities[top_indices]
        else:
            # No results above threshold, return empty
            logger.warning(f"No results above threshold {threshold} for query: {query[:50]}...")
            return []

        # Build results
        results = []
        for idx, score in zip(final_indices, final_scores):
            tool_name = self._tool_names_list[idx]
            tool_emb = self._tools[tool_name]

            results.append(SemanticSearchResult(
                tool_name=tool_name,
                tool_category=tool_emb.tool_category,
                relevance_score=float(score),
                description=tool_emb.doc_string
            ))

        logger.info(f"Search returned {len(results)} results (threshold={threshold}, top_k={top_k})")
        return results

    def _cosine_similarity_batch(self, query_embedding: List[float]) -> np.ndarray:
        """Calculate cosine similarity between query and all tools / 计算查询与所有工具之间的余弦相似度.

        Args / 参数：
            query_embedding: Query embedding vector / 查询嵌入向量

        Returns / 返回：
            np.ndarray: Similarity scores for all tools / 所有工具的相似度分数
        """
        if self._tool_embeddings_matrix is None:
            raise ValueError("Embeddings matrix not initialized")

        query_vec = np.array(query_embedding, dtype=np.float32)

        # Normalize vectors
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return np.zeros(len(self._tool_names_list))

        query_vec_normalized = query_vec / query_norm

        # Calculate dot product (equivalent to cosine similarity for normalized vectors)
        similarities = np.dot(self._tool_embeddings_matrix, query_vec_normalized)

        return similarities

    def get_tool_count(self) -> int:
        """Get total number of tools / 获取工具总数.

        Returns / 返回：
            int: Number of tools / 工具数量
        """
        return len(self._tools)

    def get_tool_categories(self) -> Dict[str, List[str]]:
        """Get all tool categories and their tools / 获取所有工具分类及其工具.

        Returns / 返回：
            Dict[str, List[str]]: Category to tools mapping / 分类到工具的映射
        """
        return TOOL_CATEGORIES

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics / 获取注册表统计信息.

        Returns / 返回：
            Dict[str, Any]: Statistics including tool count, categories, etc. / 统计信息，包括工具数量、分类等
        """
        return {
            "total_tools": len(self._tools),
            "total_categories": len(TOOL_CATEGORIES),
            "initialized": self._initialized,
            "embedding_matrix_shape": self._tool_embeddings_matrix.shape if self._tool_embeddings_matrix is not None else None,
            "config": self._config.model_dump()
        }


# Global singleton instance / 全局单例实例
semantic_registry = SemanticRegistry()