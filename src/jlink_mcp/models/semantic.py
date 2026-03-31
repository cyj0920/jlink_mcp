"""Semantic Tool Discovery Data Models / 语义工具发现数据模型.

This module defines Pydantic models for semantic tool retrieval functionality.
此模块定义了语义工具检索功能的 Pydantic 模型。

Based on the paper "Semantic Tool Discovery for Large Language Models: A Vector-Based Approach to MCP Tool Selection"
基于论文《Semantic Tool Discovery for Large Language Models: A Vector-Based Approach to MCP Tool Selection》
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class ToolEmbedding(BaseModel):
    """Tool Embedding Model / 工具嵌入模型.

    Stores metadata and embedding vector for a single tool.
    存储单个工具的元数据和嵌入向量。
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)

    tool_name: str = Field(..., description="Tool name / 工具名称")
    tool_category: str = Field(..., description="Tool category / 工具分类")
    doc_string: str = Field(..., description="Tool docstring / 工具文档字符串")
    expanded_description: str = Field(..., description="Expanded capability description / 扩展的功能描述")
    parameter_descriptions: str = Field(..., description="Parameter descriptions / 参数描述")
    embedding_vector: List[float] = Field(..., description="Embedding vector (1536 dimensions) / 嵌入向量（1536维）")

    def to_embedding_text(self) -> str:
        """Convert to text for embedding generation / 转换为用于生成嵌入的文本.

        Follows the paper's document construction template:
        遵循论文的文档构建模板：
        Tool: {tool_name}
        Purpose: {description}
        Capabilities: {expanded_description}
        Parameters: {parameter_descriptions}
        """
        return f"""Tool: {self.tool_name}
Purpose: {self.doc_string}
Capabilities: {self.expanded_description}
Parameters: {self.parameter_descriptions}"""


class SemanticSearchResult(BaseModel):
    """Semantic Search Result Model / 语义搜索结果模型.

    Represents a single tool search result with relevance score.
    表示带有相关度分数的单个工具搜索结果。
    """
    tool_name: str = Field(..., description="Tool name / 工具名称")
    tool_category: str = Field(..., description="Tool category / 工具分类")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score (0-1) / 相关度分数（0-1）")
    description: str = Field(..., description="Tool description / 工具描述")


class SemanticSearchRequest(BaseModel):
    """Semantic Search Request Model / 语义搜索请求模型.

    Validates parameters for semantic tool search.
    验证语义工具搜索的参数。
    """
    query: str = Field(..., min_length=1, description="User query in natural language / 用户自然语言查询")
    top_k: int = Field(default=3, ge=1, le=10, description="Number of tools to return / 返回工具数量")
    threshold: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Similarity threshold / 相似度阈值")


class SemanticSearchResponse(BaseModel):
    """Semantic Search Response Model / 语义搜索响应模型.

    Contains search results and metadata.
    包含搜索结果和元数据。
    """
    success: bool = Field(..., description="Search success / 搜索是否成功")
    results: List[SemanticSearchResult] = Field(default_factory=list, description="Search results / 搜索结果")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Search metadata / 搜索元数据")
    message: str = Field(default="", description="Status message / 状态消息")
    error: Optional[str] = Field(None, description="Error message / 错误消息")


class SemanticRegistryConfig(BaseModel):
    """Semantic Registry Configuration Model / 语义注册表配置模型.

    Configuration for semantic tool retrieval system.
    语义工具检索系统的配置。
    """
    enabled: bool = Field(default=False, description="Enable semantic search / 是否启用语义检索")
    embedding_model: str = Field(default="text-embedding-ada-002", description="OpenAI embedding model / OpenAI 嵌入模型")
    top_k: int = Field(default=3, ge=1, le=10, description="Default Top-K / 默认 Top-K 值")
    threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Default similarity threshold / 默认相似度阈值")
    cache_enabled: bool = Field(default=True, description="Enable embedding cache / 是否启用嵌入缓存")
    cache_version: int = Field(default=1, description="Cache version / 缓存版本")