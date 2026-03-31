"""Unit tests for semantic search functionality / 语义检索功能的单元测试.

Tests core components:
测试核心组件：
- Semantic data models / 语义数据模型
- Embedding manager / 嵌入管理器
- Semantic registry / 语义注册表
- Semantic search tools / 语义检索工具
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from jlink_mcp.models.semantic import (
    ToolEmbedding,
    SemanticSearchResult,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticRegistryConfig
)
from jlink_mcp.tools.semantic import semantic_search_tools, get_semantic_stats


class TestSemanticModels:
    """Tests for semantic data models / 语义数据模型测试."""

    def test_tool_embedding_model(self):
        """Test ToolEmbedding model / 测试 ToolEmbedding 模型."""
        emb = ToolEmbedding(
            tool_name="read_memory",
            tool_category="内存操作",
            doc_string="Read memory from device",
            expanded_description="Read memory from target device at specified address",
            parameter_descriptions="address: start address, size: bytes to read",
            embedding_vector=[0.0] * 1536
        )

        assert emb.tool_name == "read_memory"
        assert emb.tool_category == "内存操作"
        assert len(emb.embedding_vector) == 1536

    def test_tool_embedding_to_text(self):
        """Test ToolEmbedding.to_embedding_text() / 测试 ToolEmbedding.to_embedding_text()."""
        emb = ToolEmbedding(
            tool_name="read_memory",
            tool_category="内存操作",
            doc_string="Read memory",
            expanded_description="Read memory from device",
            parameter_descriptions="address: start address",
            embedding_vector=[0.0] * 1536
        )

        text = emb.to_embedding_text()
        assert "Tool: read_memory" in text
        assert "Purpose: Read memory" in text
        assert "Capabilities: Read memory from device" in text
        assert "Parameters: address: start address" in text

    def test_semantic_search_result_model(self):
        """Test SemanticSearchResult model / 测试 SemanticSearchResult 模型."""
        result = SemanticSearchResult(
            tool_name="read_memory",
            tool_category="内存操作",
            relevance_score=0.95,
            description="Read memory from device"
        )

        assert result.tool_name == "read_memory"
        assert result.relevance_score == 0.95
        assert 0.0 <= result.relevance_score <= 1.0

    def test_semantic_search_request_model(self):
        """Test SemanticSearchRequest model / 测试 SemanticSearchRequest 模型."""
        req = SemanticSearchRequest(
            query="read register",
            top_k=3,
            threshold=0.5
        )

        assert req.query == "read register"
        assert req.top_k == 3
        assert req.threshold == 0.5

    def test_semantic_search_request_validation(self):
        """Test SemanticSearchRequest validation / 测试 SemanticSearchRequest 验证."""
        # Valid request
        req = SemanticSearchRequest(query="test", top_k=5, threshold=0.7)
        assert req.query == "test"

        # Invalid: empty query
        with pytest.raises(Exception):
            SemanticSearchRequest(query="", top_k=3)

        # Invalid: top_k out of range
        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", top_k=0)

        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", top_k=11)

        # Invalid: threshold out of range
        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", threshold=-0.1)

        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", threshold=1.1)

    def test_semantic_registry_config_model(self):
        """Test SemanticRegistryConfig model / 测试 SemanticRegistryConfig 模型."""
        config = SemanticRegistryConfig()

        assert config.enabled is False
        assert config.embedding_model == "text-embedding-ada-002"
        assert config.top_k == 3
        assert config.threshold == 0.5
        assert config.cache_enabled is True

    def test_semantic_search_response_model(self):
        """Test SemanticSearchResponse model / 测试 SemanticSearchResponse 模型."""
        response = SemanticSearchResponse(
            success=True,
            results=[
                SemanticSearchResult(
                    tool_name="read_memory",
                    tool_category="内存操作",
                    relevance_score=0.95,
                    description="Read memory"
                )
            ],
            metadata={"query": "read memory"},
            message="Success"
        )

        assert response.success is True
        assert len(response.results) == 1
        assert response.metadata["query"] == "read memory"


class TestSemanticSearchTools:
    """Tests for semantic search tool functions / 语义检索工具函数测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_semantic_search_tools_success(self, mock_config, mock_registry):
        """Test semantic_search_tools() success case / 测试 semantic_search_tools() 成功情况."""
        # Setup mocks
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="read_memory",
                tool_category="内存操作",
                relevance_score=0.95,
                description="Read memory"
            )
        ]
        mock_registry.get_tool_count.return_value = 41

        # Call function
        result = semantic_search_tools("read memory", top_k=3, threshold=0.5)

        # Verify
        assert result["success"] is True
        assert len(result["results"]) == 1
        assert result["results"][0]["tool_name"] == "read_memory"
        assert result["metadata"]["query"] == "read memory"
        assert result["metadata"]["total_tools"] == 41

    def test_semantic_search_tools_disabled(self):
        """Test semantic_search_tools() when disabled / 测试语义检索禁用时的行为."""
        with patch('jlink_mcp.config_manager.config_manager') as mock_config:
            mock_config.get_config.return_value = Mock(semantic_enabled=False)

            result = semantic_search_tools("read memory")

            assert result["success"] is False
            assert "disabled" in result["error"].lower()

    def test_semantic_search_tools_empty_query(self):
        """Test semantic_search_tools() with empty query / 测试空查询."""
        result = semantic_search_tools("")

        assert result["success"] is False
        assert "empty" in result["error"].lower()

    def test_semantic_search_tools_invalid_top_k(self):
        """Test semantic_search_tools() with invalid top_k / 测试无效的 top_k."""
        result = semantic_search_tools("read memory", top_k=0)

        assert result["success"] is False
        assert "top_k" in result["error"].lower()

        result = semantic_search_tools("read memory", top_k=11)

        assert result["success"] is False
        assert "top_k" in result["error"].lower()

    def test_semantic_search_tools_invalid_threshold(self):
        """Test semantic_search_tools() with invalid threshold / 测试无效的阈值."""
        result = semantic_search_tools("read memory", threshold=-0.1)

        assert result["success"] is False
        assert "threshold" in result["error"].lower()

        result = semantic_search_tools("read memory", threshold=1.1)

        assert result["success"] is False
        assert "threshold" in result["error"].lower()

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    def test_get_semantic_stats_success(self, mock_registry):
        """Test get_semantic_stats() success case / 测试 get_semantic_stats() 成功情况."""
        mock_registry.get_stats.return_value = {
            "total_tools": 41,
            "total_categories": 8,
            "initialized": True
        }

        result = get_semantic_stats()

        assert result["success"] is True
        assert result["data"]["total_tools"] == 41

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    def test_get_semantic_stats_failure(self, mock_registry):
        """Test get_semantic_stats() failure case / 测试 get_semantic_stats() 失败情况."""
        mock_registry.get_stats.side_effect = Exception("Test error")

        result = get_semantic_stats()

        assert result["success"] is False
        assert result["error"] == "Test error"


class TestCosineSimilarity:
    """Tests for cosine similarity calculation / 余弦相似度计算测试."""

    def test_cosine_similarity_identical(self):
        """Test cosine similarity of identical vectors / 测试相同向量的余弦相似度."""
        import numpy as np

        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([1.0, 2.0, 3.0])

        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        assert abs(similarity - 1.0) < 1e-6

    def test_cosine_similarity_orthogonal(self):
        """Test cosine similarity of orthogonal vectors / 测试正交向量的余弦相似度."""
        import numpy as np

        vec1 = np.array([1.0, 0.0, 0.0])
        vec2 = np.array([0.0, 1.0, 0.0])

        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        assert abs(similarity - 0.0) < 1e-6

    def test_cosine_similarity_opposite(self):
        """Test cosine similarity of opposite vectors / 测试相反向量的余弦相似度."""
        import numpy as np

        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([-1.0, -2.0, -3.0])

        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        assert abs(similarity - (-1.0)) < 1e-6

    def test_cosine_similarity_partial(self):
        """Test cosine similarity of partially similar vectors / 测试部分相似向量的余弦相似度."""
        import numpy as np

        vec1 = np.array([1.0, 2.0, 3.0])
        vec2 = np.array([2.0, 4.0, 6.0])  # Scaled version

        similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
        assert abs(similarity - 1.0) < 1e-6  # Scaled vectors should have similarity = 1.0


@pytest.mark.unit
class TestSemanticIntegration:
    """Integration tests for semantic search / 语义检索集成测试."""

    def test_semantic_search_end_to_end_mock(self):
        """Test end-to-end semantic search with mocks / 使用 Mock 测试端到端语义检索."""
        with patch('jlink_mcp.semantic_registry.semantic_registry') as mock_registry:
            with patch('jlink_mcp.config_manager.config_manager') as mock_config:
                # Setup
                mock_config.get_config.return_value = Mock(semantic_enabled=True)
                mock_registry.search.return_value = [
                    SemanticSearchResult(
                        tool_name="read_memory",
                        tool_category="内存操作",
                        relevance_score=0.95,
                        description="Read memory"
                    ),
                    SemanticSearchResult(
                        tool_name="read_registers",
                        tool_category="内存操作",
                        relevance_score=0.90,
                        description="Read registers"
                    )
                ]
                mock_registry.get_tool_count.return_value = 41

                # Execute
                result = semantic_search_tools("read data", top_k=3, threshold=0.5)

                # Verify
                assert result["success"] is True
                assert len(result["results"]) == 2
                assert result["results"][0]["relevance_score"] >= result["results"][1]["relevance_score"]
                assert result["metadata"]["token_savings"] == "95.1%"  # (1 - 2/41) * 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])