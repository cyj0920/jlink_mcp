"""Semantic Search Tool Functions / 语义搜索工具函数.

This module provides semantic tool discovery functionality.
此模块提供语义工具发现功能。

Based on the paper "Semantic Tool Discovery for Large Language Models: A Vector-Based Approach to MCP Tool Selection"
基于论文《Semantic Tool Discovery for Large Language Models: A Vector-Based Approach to MCP Tool Selection》

Features / 功能：
- Semantic search for tools using natural language queries / 使用自然语言查询进行语义工具搜索
- Reduce token consumption by 95-99% / 减少 95-99% 的 Token 消耗
- Improve tool selection accuracy / 提高工具选择准确率
"""

from typing import Dict, Any

from ..semantic_registry import semantic_registry
from ..config_manager import config_manager
from ..utils import logger


def semantic_search_tools(
    query: str,
    top_k: int = 3,
    threshold: float = 0.5
) -> Dict[str, Any]:
    """Semantic Search Tools - Recommend relevant tools based on natural language query / 语义搜索工具 - 根据自然语言查询推荐相关工具.

    Uses vector embedding technology to intelligently match user queries with available tools.
    使用向量嵌入技术，智能匹配用户查询与可用工具。

    This can significantly reduce AI model token consumption (expected 95-99% savings).
    可以大幅减少 AI 模型的 Token 消耗（预期节省 95-99%）。

    Examples / 示例：
        - "如何读取寄存器?" (How to read registers?) → Returns read_registers, read_register_with_fields
        - "如何烧录固件?" (How to flash firmware?) → Returns erase_flash, program_flash, verify_flash
        - "如何查看实时日志?" (How to view real-time logs?) → Returns rtt_start, rtt_read
        - "read memory" → Returns read_memory, read_registers
        - "connect to device" → Returns connect_device, list_jlink_devices

    Args / 参数：
        query: User query in natural language (Chinese or English) / 用户自然语言查询（中文或英文）
        top_k: Number of tools to return (default: 3, range: 1-10) / 返回工具数量（默认：3，范围：1-10）
        threshold: Similarity threshold (default: 0.5, range: 0-1) / 相似度阈值（默认：0.5，范围：0-1）

    Returns / 返回：
        Dict[str, Any]: Search results containing / 搜索结果包含：
            - success (bool): Whether search succeeded / 搜索是否成功
            - results (list): List of relevant tools with scores / 相关工具列表及分数
            - metadata (dict): Search metadata including query, total tools, etc. / 搜索元数据，包括查询、工具总数等
            - message (str): Status message / 状态消息
            - error (str): Error message if failed / 失败时的错误消息

    Raises / 异常：
        ValueError: If query is empty or parameters are invalid / 如果查询为空或参数无效
        RuntimeError: If semantic search is not enabled / 如果未启用语义检索

    Notes / 注意：
        - This tool requires OpenAI API key to be configured / 此工具需要配置 OpenAI API Key
        - First search will generate embeddings for all tools (may take 1-2 seconds) / 首次搜索将为所有工具生成嵌入（可能需要 1-2 秒）
        - Subsequent searches will be fast (<50ms) due to caching / 后续搜索将很快（<50ms），因为缓存
        - Supports both Chinese and English queries / 支持中文和英文查询
    """
    try:
        # Validate parameters
        if not query or not query.strip():
            return {
                "success": False,
                "results": [],
                "metadata": {},
                "message": "Query cannot be empty",
                "error": "Query cannot be empty / 查询不能为空"
            }

        if top_k < 1 or top_k > 10:
            return {
                "success": False,
                "results": [],
                "metadata": {},
                "message": "top_k must be between 1 and 10",
                "error": "top_k must be between 1 and 10 / top_k 必须在 1-10 之间"
            }

        if threshold < 0.0 or threshold > 1.0:
            return {
                "success": False,
                "results": [],
                "metadata": {},
                "message": "threshold must be between 0 and 1",
                "error": "threshold must be between 0 and 1 / threshold 必须在 0-1 之间"
            }

        # Check if semantic search is enabled
        cfg = config_manager.get_config()
        if hasattr(cfg, 'semantic_enabled') and not cfg.semantic_enabled:
            logger.warning("Semantic search is disabled in config")
            return {
                "success": False,
                "results": [],
                "metadata": {},
                "message": "Semantic search is disabled",
                "error": "Semantic search is disabled in config. Enable it by setting config.semantic_enabled = True / 语义检索在配置中已禁用。通过设置 config.semantic_enabled = True 启用它"
            }

        # Perform semantic search
        logger.info(f"Performing semantic search: query='{query[:50]}...', top_k={top_k}, threshold={threshold}")
        results = semantic_registry.search(query, top_k=top_k, threshold=threshold)

        # Build response
        total_tools = semantic_registry.get_tool_count()

        return {
            "success": True,
            "results": [
                {
                    "tool_name": r.tool_name,
                    "tool_category": r.tool_category,
                    "relevance_score": round(r.relevance_score, 4),
                    "description": r.description
                }
                for r in results
            ],
            "metadata": {
                "query": query,
                "top_k": top_k,
                "threshold": threshold,
                "total_tools": total_tools,
                "candidates": len(results),
                "token_savings": f"{round((1 - len(results) / total_tools) * 100, 1)}%"
            },
            "message": f"Found {len(results)} relevant tools out of {total_tools} total tools"
        }

    except ValueError as e:
        logger.error(f"Semantic search parameter error: {e}")
        return {
            "success": False,
            "results": [],
            "metadata": {},
            "message": "Invalid parameters",
            "error": str(e)
        }

    except Exception as e:
        logger.error(f"Semantic search failed: {e}", exc_info=True)
        return {
            "success": False,
            "results": [],
            "metadata": {},
            "message": "Semantic search failed",
            "error": f"{str(e)} / 语义搜索失败"
        }


def get_semantic_stats() -> Dict[str, Any]:
    """Get Semantic Search Statistics / 获取语义搜索统计信息.

    Returns statistics about the semantic search system including:
    返回语义搜索系统的统计信息，包括：
    - Total number of tools / 工具总数
    - Number of categories / 分类数量
    - Initialization status / 初始化状态
    - Embedding cache statistics / 嵌入缓存统计

    Returns / 返回：
        Dict[str, Any]: Statistics / 统计信息
    """
    try:
        registry_stats = semantic_registry.get_stats()

        return {
            "success": True,
            "data": registry_stats,
            "message": "Statistics retrieved successfully"
        }

    except Exception as e:
        logger.error(f"Failed to get semantic stats: {e}")
        return {
            "success": False,
            "data": None,
            "message": "Failed to retrieve statistics",
            "error": str(e)
        }