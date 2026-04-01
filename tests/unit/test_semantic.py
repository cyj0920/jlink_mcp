"""Unit tests for semantic search functionality / 语义检索功能的单元测试."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from jlink_mcp.embedding_manager import EmbeddingManager
from jlink_mcp.models.semantic import (
    SemanticRegistryConfig,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResult,
    ToolEmbedding,
)
from jlink_mcp.semantic_registry import semantic_registry
from jlink_mcp.tools import semantic as semantic_tools


@pytest.fixture
def reset_registry_state():
    """Reset singleton registry state after each test / 每个测试后重置注册表单例状态."""
    registry = semantic_registry
    old_tools = registry._tools
    old_matrix = registry._tool_embeddings_matrix
    old_names = registry._tool_names_list
    old_initialized = registry._initialized
    old_embedding_manager = registry._embedding_manager

    registry._tools = {}
    registry._tool_embeddings_matrix = None
    registry._tool_names_list = []
    registry._initialized = False

    try:
        yield registry
    finally:
        registry._tools = old_tools
        registry._tool_embeddings_matrix = old_matrix
        registry._tool_names_list = old_names
        registry._initialized = old_initialized
        registry._embedding_manager = old_embedding_manager


@pytest.mark.unit
class TestSemanticModels:
    """Tests for semantic data models / 语义数据模型测试."""

    def test_tool_embedding_model(self):
        emb = ToolEmbedding(
            tool_name="read_memory",
            tool_category="内存操作",
            doc_string="Read memory from device",
            expanded_description="Read memory from target device at specified address",
            parameter_descriptions="address: start address; size: int",
            embedding_vector=[0.0] * 3,
        )

        assert emb.tool_name == "read_memory"
        assert emb.tool_category == "内存操作"
        assert len(emb.embedding_vector) == 3

    def test_tool_embedding_to_text(self):
        emb = ToolEmbedding(
            tool_name="read_memory",
            tool_category="内存操作",
            doc_string="Read memory",
            expanded_description="Read memory from device",
            parameter_descriptions="address: int",
            embedding_vector=[0.0] * 3,
        )

        text = emb.to_embedding_text()
        assert "Tool: read_memory" in text
        assert "Purpose: Read memory" in text
        assert "Capabilities: Read memory from device" in text
        assert "Parameters: address: int" in text

    def test_semantic_search_request_validation(self):
        req = SemanticSearchRequest(query="read register", top_k=3, threshold=0.5)
        assert req.query == "read register"

        with pytest.raises(Exception):
            SemanticSearchRequest(query="", top_k=3)

        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", top_k=0)

        with pytest.raises(Exception):
            SemanticSearchRequest(query="test", threshold=1.1)

    def test_semantic_registry_config_model(self):
        config = SemanticRegistryConfig()
        assert config.enabled is False
        assert config.embedding_model == "text-embedding-ada-002"
        assert config.top_k == 3
        assert config.threshold == 0.5
        assert config.cache_enabled is True

    def test_semantic_search_response_model(self):
        response = SemanticSearchResponse(
            success=True,
            results=[
                SemanticSearchResult(
                    tool_name="read_memory",
                    tool_category="内存操作",
                    relevance_score=0.95,
                    description="Read memory",
                )
            ],
            metadata={"query": "read memory"},
            message="Success",
        )

        assert response.success is True
        assert response.results[0].tool_name == "read_memory"
        assert response.metadata["query"] == "read memory"


@pytest.mark.unit
class TestEmbeddingManager:
    """Tests for embedding manager behavior / 嵌入管理器行为测试."""

    def test_cache_path_uses_user_cache_directory(self, monkeypatch, tmp_path):
        monkeypatch.setenv("JLINK_MCP_CACHE_DIR", str(tmp_path))
        monkeypatch.setattr(EmbeddingManager, "_instance", None)
        monkeypatch.setattr(EmbeddingManager, "_initialized", False)

        manager = EmbeddingManager()

        assert manager._cache_file.parent == tmp_path / "jlink_mcp"
        assert str(manager._cache_file).startswith(str(tmp_path))


@pytest.mark.unit
class TestSemanticRegistry:
    """Tests for semantic registry internals / 语义注册表内部测试."""

    def test_discover_mcp_tools_reads_real_server_definitions(self, reset_registry_state):
        discovered = reset_registry_state._discover_mcp_tools()
        names = {tool["tool_name"] for tool in discovered}
        connect_device = next(tool for tool in discovered if tool["tool_name"] == "connect_device")

        assert "semantic_search_tools" in names
        assert "get_semantic_stats" in names
        assert "get_usage_guidance" in names
        assert "get_system_prompt" in names
        assert "serial_number" in connect_device["parameter_descriptions"]
        assert "chip_name" in connect_device["parameter_descriptions"]

    def test_initialize_populates_tools_and_embeddings(self, monkeypatch, reset_registry_state):
        fake_tools = [
            {
                "tool_name": "tool_a",
                "doc_string": "Tool A summary",
                "full_doc_string": "Tool A summary\nAdditional details",
                "parameter_descriptions": "address: int",
            },
            {
                "tool_name": "tool_b",
                "doc_string": "Tool B summary",
                "full_doc_string": "Tool B summary\nAdditional details",
                "parameter_descriptions": "value: int = 1",
            },
        ]

        fake_embedding_manager = Mock()
        fake_embedding_manager.get_batch_embeddings.return_value = [[1.0, 0.0], [0.0, 1.0]]

        monkeypatch.setattr(reset_registry_state, "_discover_mcp_tools", lambda: fake_tools)
        reset_registry_state._embedding_manager = fake_embedding_manager

        reset_registry_state.initialize()

        assert reset_registry_state._initialized is True
        assert reset_registry_state.get_tool_count() == 2
        assert reset_registry_state._tool_embeddings_matrix is not None
        assert reset_registry_state._tool_embeddings_matrix.shape == (2, 2)
        fake_embedding_manager.get_batch_embeddings.assert_called_once()

    def test_search_uses_normalized_cosine_similarity(self, monkeypatch, reset_registry_state):
        fake_tools = [
            {
                "tool_name": "strong_x",
                "doc_string": "Strong X",
                "full_doc_string": "Strong X",
                "parameter_descriptions": "query: str",
            },
            {
                "tool_name": "diagonal",
                "doc_string": "Diagonal",
                "full_doc_string": "Diagonal",
                "parameter_descriptions": "query: str",
            },
        ]

        class FakeEmbeddingManager:
            def get_batch_embeddings(self, texts):
                assert len(texts) == 2
                return [[10.0, 0.0], [1.0, 1.0]]

            def get_embedding(self, text):
                assert text == "x axis"
                return [1.0, 0.0]

        monkeypatch.setattr(reset_registry_state, "_discover_mcp_tools", lambda: fake_tools)
        reset_registry_state._embedding_manager = FakeEmbeddingManager()
        reset_registry_state.initialize()

        results = reset_registry_state.search("x axis", top_k=2, threshold=0.5)

        assert [item.tool_name for item in results] == ["strong_x", "diagonal"]
        assert results[0].relevance_score == pytest.approx(1.0, abs=1e-6)
        assert results[1].relevance_score == pytest.approx(0.7071, abs=1e-4)


@pytest.mark.unit
class TestSemanticSearchTools:
    """Tests for tool-facing semantic helpers / 面向工具层的语义检索辅助函数测试."""

    def test_semantic_search_tools_success(self, monkeypatch):
        mock_registry = Mock()
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="read_memory",
                tool_category="内存操作",
                relevance_score=0.95,
                description="Read memory",
            )
        ]
        mock_registry.get_tool_count.return_value = 43

        monkeypatch.setattr(semantic_tools, "semantic_registry", mock_registry)
        monkeypatch.setattr(
            semantic_tools,
            "config_manager",
            SimpleNamespace(get_config=lambda: SimpleNamespace(semantic_enabled=True)),
        )

        result = semantic_tools.semantic_search_tools("read memory", top_k=3, threshold=0.5)

        assert result["success"] is True
        assert result["results"][0]["tool_name"] == "read_memory"
        assert result["metadata"]["total_tools"] == 43
        assert result["metadata"]["token_savings"] == "97.7%"

    def test_semantic_search_tools_disabled(self, monkeypatch):
        monkeypatch.setattr(
            semantic_tools,
            "config_manager",
            SimpleNamespace(get_config=lambda: SimpleNamespace(semantic_enabled=False)),
        )

        result = semantic_tools.semantic_search_tools("read memory")

        assert result["success"] is False
        assert "disabled" in result["error"].lower()

    def test_semantic_search_tools_validation(self):
        assert semantic_tools.semantic_search_tools("")["success"] is False
        assert semantic_tools.semantic_search_tools("read memory", top_k=0)["success"] is False
        assert semantic_tools.semantic_search_tools("read memory", threshold=2.0)["success"] is False

    def test_get_semantic_stats_success(self, monkeypatch):
        mock_registry = Mock()
        mock_registry.get_stats.return_value = {
            "total_tools": 43,
            "total_categories": 11,
            "initialized": True,
        }
        monkeypatch.setattr(semantic_tools, "semantic_registry", mock_registry)

        result = semantic_tools.get_semantic_stats()

        assert result["success"] is True
        assert result["data"]["total_tools"] == 43

    def test_get_semantic_stats_failure(self, monkeypatch):
        mock_registry = Mock()
        mock_registry.get_stats.side_effect = RuntimeError("boom")
        monkeypatch.setattr(semantic_tools, "semantic_registry", mock_registry)

        result = semantic_tools.get_semantic_stats()

        assert result["success"] is False
        assert result["error"] == "boom"
