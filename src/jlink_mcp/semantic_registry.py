"""Semantic Tool Registry Module / 语义工具注册表模块.

This module manages tool metadata and provides semantic search functionality.
此模块管理工具元数据并提供语义搜索功能。

Features / 功能：
- Discover real MCP tools from server.py / 从 server.py 发现真实 MCP 工具
- Build tool documents with docstrings and parameters / 用文档字符串和参数构建工具文档
- Generate embeddings for all tools / 为所有工具生成嵌入
- Perform semantic search using cosine similarity / 使用余弦相似度执行语义搜索
- Singleton pattern for global access / 单例模式以实现全局访问
"""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np

from .embedding_manager import embedding_manager
from .models.semantic import SemanticRegistryConfig, SemanticSearchResult, ToolEmbedding
from .tools.guidance import TOOL_CATEGORIES, USAGE_SCENARIOS
from .utils import logger


class SemanticRegistry:
    """Semantic Tool Registry (Singleton Pattern) / 语义工具注册表（单例模式）."""

    _instance: Optional["SemanticRegistry"] = None
    _singleton_ready: bool = False

    def __new__(cls) -> "SemanticRegistry":
        """Singleton pattern implementation / 单例模式实现."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize semantic registry state / 初始化语义注册表状态."""
        if SemanticRegistry._singleton_ready:
            return

        self._tools: Dict[str, ToolEmbedding] = {}
        self._tool_embeddings_matrix: Optional[np.ndarray] = None
        self._tool_names_list: List[str] = []
        self._config: SemanticRegistryConfig = SemanticRegistryConfig()
        self._embedding_manager = embedding_manager
        self._initialized = False

        SemanticRegistry._singleton_ready = True
        logger.info("SemanticRegistry instance created")

    def initialize(self, force: bool = False) -> None:
        """Initialize registry: discover tools and generate embeddings / 初始化注册表：发现工具并生成嵌入."""
        if self._initialized and not force:
            logger.info("Registry already initialized, skipping")
            return

        logger.info("Initializing semantic registry...")
        self._tools = {}
        self._tool_embeddings_matrix = None
        self._tool_names_list = []

        self._scan_tools()
        self._generate_embeddings()
        self._build_embeddings_matrix()

        self._initialized = True
        logger.info(f"Semantic registry initialized with {len(self._tools)} tools")

    def _scan_tools(self) -> None:
        """Scan MCP tool definitions from server.py / 从 server.py 扫描 MCP 工具定义."""
        category_map = self._build_category_map()
        discovered_tools = self._discover_mcp_tools()

        logger.info(
            "Discovered %s MCP tools in server.py across %s configured categories",
            len(discovered_tools),
            len(TOOL_CATEGORIES),
        )

        for tool_info in discovered_tools:
            tool_name = tool_info["tool_name"]
            category = category_map.get(tool_name, self._infer_category(tool_name))
            self._tools[tool_name] = self._build_tool_metadata(tool_info, category)

    def _build_category_map(self) -> Dict[str, str]:
        """Build tool-to-category mapping / 构建工具到分类的映射."""
        category_map: Dict[str, str] = {}
        for category_name, category_info in TOOL_CATEGORIES.items():
            for tool_name in category_info["tools"]:
                category_map[tool_name] = category_name
        return category_map

    def _discover_mcp_tools(self) -> List[Dict[str, Any]]:
        """Discover actual MCP tools by parsing server.py / 通过解析 server.py 发现真实 MCP 工具."""
        server_file = Path(__file__).with_name("server.py")
        source = server_file.read_text(encoding="utf-8")
        module = ast.parse(source, filename=str(server_file))

        tools: List[Dict[str, Any]] = []
        for node in module.body:
            if isinstance(node, ast.AsyncFunctionDef) and self._is_mcp_tool(node):
                docstring = ast.get_docstring(node) or ""
                tools.append(
                    {
                        "tool_name": node.name,
                        "doc_string": self._extract_summary(docstring, node.name),
                        "full_doc_string": self._normalize_docstring(docstring),
                        "parameter_descriptions": self._build_parameter_descriptions(node),
                    }
                )

        return tools

    def _is_mcp_tool(self, node: ast.AsyncFunctionDef) -> bool:
        """Check whether function is decorated with @mcp.tool() / 判断函数是否被 @mcp.tool() 装饰."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                func = decorator.func
                if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name):
                    if func.value.id == "mcp" and func.attr == "tool":
                        return True
        return False

    def _extract_summary(self, docstring: str, tool_name: str) -> str:
        """Extract one-line summary from docstring / 从文档字符串中提取单行摘要."""
        normalized = self._normalize_docstring(docstring)
        if not normalized:
            return tool_name.replace("_", " ")

        first_line = normalized.splitlines()[0].strip()
        return first_line or tool_name.replace("_", " ")

    def _normalize_docstring(self, docstring: str) -> str:
        """Normalize docstring for embedding text / 规范化文档字符串用于嵌入文本."""
        lines = [line.strip() for line in docstring.splitlines()]
        return "\n".join(line for line in lines if line)

    def _build_parameter_descriptions(self, node: ast.AsyncFunctionDef) -> str:
        """Build parameter descriptions from function signature / 从函数签名构建参数描述."""
        positional_args = list(node.args.args)
        defaults = list(node.args.defaults)
        default_offset = len(positional_args) - len(defaults)
        default_map = {
            positional_args[index + default_offset].arg: defaults[index]
            for index in range(len(defaults))
        }

        parts: List[str] = []
        for arg in positional_args:
            if arg.arg == "self":
                continue
            parts.append(self._format_arg(arg.arg, arg.annotation, default_map.get(arg.arg)))

        if node.args.vararg is not None:
            parts.append(self._format_arg(f"*{node.args.vararg.arg}", node.args.vararg.annotation, None))

        kw_defaults = list(node.args.kw_defaults)
        for arg, default in zip(node.args.kwonlyargs, kw_defaults):
            parts.append(self._format_arg(arg.arg, arg.annotation, default))

        if node.args.kwarg is not None:
            parts.append(self._format_arg(f"**{node.args.kwarg.arg}", node.args.kwarg.annotation, None))

        return "; ".join(parts) if parts else "No parameters"

    def _format_arg(self, name: str, annotation: Optional[ast.expr], default: Optional[ast.expr]) -> str:
        """Format one parameter description / 格式化单个参数描述."""
        annotation_text = ast.unparse(annotation) if annotation is not None else "Any"
        if default is None:
            return f"{name}: {annotation_text}"
        return f"{name}: {annotation_text} = {ast.unparse(default)}"

    def _build_tool_metadata(self, tool_info: Dict[str, Any], category: str) -> ToolEmbedding:
        """Build tool metadata / 构建工具元数据."""
        tool_name = str(tool_info["tool_name"])
        doc_string = str(tool_info["doc_string"])
        full_doc_string = str(tool_info.get("full_doc_string", doc_string))
        parameter_descriptions = str(tool_info["parameter_descriptions"])
        expanded_description = self._build_expanded_description(tool_name, doc_string, full_doc_string)

        return ToolEmbedding(
            tool_name=tool_name,
            tool_category=category,
            doc_string=doc_string,
            expanded_description=expanded_description,
            parameter_descriptions=parameter_descriptions,
            embedding_vector=[],
        )

    def _build_expanded_description(self, tool_name: str, doc_string: str, full_doc_string: str) -> str:
        """Build expanded description from docstring and scenarios / 从文档字符串和场景构建扩展描述."""
        descriptions: List[str] = []

        category_map = self._build_category_map()
        category = category_map.get(tool_name)
        if category and category in TOOL_CATEGORIES:
            descriptions.append(TOOL_CATEGORIES[category]["description"])

        for scenario_info in USAGE_SCENARIOS.values():
            steps_str = " ".join(scenario_info.get("steps", []))
            if tool_name in steps_str:
                descriptions.append(scenario_info["description"])

        if full_doc_string and full_doc_string != doc_string:
            descriptions.append(full_doc_string)
        elif doc_string:
            descriptions.append(doc_string)

        unique_descriptions: List[str] = []
        for item in descriptions:
            if item and item not in unique_descriptions:
                unique_descriptions.append(item)

        return " ".join(unique_descriptions) if unique_descriptions else f"Functionality for {tool_name}"

    def _infer_category(self, tool_name: str) -> str:
        """Infer category for tools missing from TOOL_CATEGORIES / 推断未在 TOOL_CATEGORIES 中声明的工具分类."""
        if tool_name.startswith("semantic_") or tool_name.startswith("get_semantic_"):
            return "语义检索"
        if "prompt" in tool_name:
            return "系统提示词"
        if tool_name.startswith("get_") or tool_name.startswith("list_"):
            return "使用指南"
        return "其他"

    def _generate_embeddings(self) -> None:
        """Generate embeddings for all tools / 为所有工具生成嵌入."""
        if not self._tools:
            logger.warning("No tools discovered, skipping embedding generation")
            return

        logger.info(f"Generating embeddings for {len(self._tools)} tools...")
        tool_names = list(self._tools.keys())
        texts = [self._tools[tool_name].to_embedding_text() for tool_name in tool_names]

        embeddings = self._embedding_manager.get_batch_embeddings(texts)
        for tool_name, embedding in zip(tool_names, embeddings):
            self._tools[tool_name].embedding_vector = embedding

        logger.info(f"Generated embeddings for {len(embeddings)} tools")

    def _build_embeddings_matrix(self) -> None:
        """Build normalized embeddings matrix / 构建归一化后的嵌入矩阵."""
        if not self._tools:
            return

        self._tool_names_list = list(self._tools.keys())
        embeddings = np.array(
            [self._tools[name].embedding_vector for name in self._tool_names_list],
            dtype=np.float32,
        )

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self._tool_embeddings_matrix = embeddings / norms

        logger.info(f"Built embeddings matrix: {self._tool_embeddings_matrix.shape}")

    def search(self, query: str, top_k: int = 3, threshold: float = 0.5) -> List[SemanticSearchResult]:
        """Perform semantic search / 执行语义搜索."""
        if not self._initialized:
            self.initialize()

        if self._tool_embeddings_matrix is None or not self._tool_names_list:
            logger.warning("Semantic registry is initialized without embeddings")
            return []

        logger.debug(f"Generating embedding for query: {query[:50]}...")
        query_embedding = self._embedding_manager.get_embedding(query)
        similarities = self._cosine_similarity_batch(query_embedding)

        above_threshold = similarities >= threshold
        if not np.any(above_threshold):
            logger.warning(f"No results above threshold {threshold} for query: {query[:50]}...")
            return []

        valid_indices = np.where(above_threshold)[0]
        valid_similarities = similarities[valid_indices]
        top_indices = np.argsort(valid_similarities)[::-1][:top_k]
        final_indices = valid_indices[top_indices]
        final_scores = valid_similarities[top_indices]

        results: List[SemanticSearchResult] = []
        for idx, score in zip(final_indices, final_scores):
            tool_name = self._tool_names_list[idx]
            tool_emb = self._tools[tool_name]
            results.append(
                SemanticSearchResult(
                    tool_name=tool_name,
                    tool_category=tool_emb.tool_category,
                    relevance_score=float(np.clip(score, 0.0, 1.0)),
                    description=tool_emb.doc_string,
                )
            )

        logger.info(f"Search returned {len(results)} results (threshold={threshold}, top_k={top_k})")
        return results

    def _cosine_similarity_batch(self, query_embedding: List[float]) -> np.ndarray:
        """Calculate cosine similarity between query and all tools / 计算查询与所有工具之间的余弦相似度."""
        if self._tool_embeddings_matrix is None:
            raise ValueError("Embeddings matrix not initialized")

        query_vec = np.array(query_embedding, dtype=np.float32)
        query_norm = np.linalg.norm(query_vec)
        if query_norm == 0:
            return np.zeros(len(self._tool_names_list), dtype=np.float32)

        query_vec_normalized = query_vec / query_norm
        similarities = np.dot(self._tool_embeddings_matrix, query_vec_normalized)
        return np.clip(similarities, -1.0, 1.0)

    def get_tool_count(self) -> int:
        """Get total number of tools / 获取工具总数."""
        return len(self._tools)

    def get_tool_categories(self) -> Dict[str, List[str]]:
        """Get all tool categories and their tools / 获取所有工具分类及其工具."""
        if not self._tools:
            return TOOL_CATEGORIES

        categories: Dict[str, List[str]] = {}
        for tool in self._tools.values():
            categories.setdefault(tool.tool_category, []).append(tool.tool_name)
        return categories

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics / 获取注册表统计信息."""
        return {
            "total_tools": len(self._tools),
            "total_categories": len(self.get_tool_categories()),
            "initialized": self._initialized,
            "embedding_matrix_shape": self._tool_embeddings_matrix.shape if self._tool_embeddings_matrix is not None else None,
            "config": self._config.model_dump(),
        }


semantic_registry = SemanticRegistry()
