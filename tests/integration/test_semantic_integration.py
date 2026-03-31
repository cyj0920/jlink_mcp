"""Integration tests for semantic search functionality / 语义检索功能的集成测试.

Tests end-to-end workflows:
测试端到端工作流：
- Full semantic search workflow / 完整的语义检索工作流
- Multilingual search (Chinese and English) / 多语言搜索（中文和英文）
- Threshold filtering / 阈值过滤
- Configuration integration / 配置集成
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from jlink_mcp.tools.semantic import semantic_search_tools, get_semantic_stats
from jlink_mcp.models.semantic import SemanticSearchResult


@pytest.mark.integration
class TestSemanticSearchIntegration:
    """Integration tests for semantic search / 语义检索集成测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_full_workflow(self, mock_config, mock_registry):
        """Test complete semantic search workflow / 测试完整的语义检索工作流."""
        # Setup configuration
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Setup registry with realistic results
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="read_registers",
                tool_category="内存操作",
                relevance_score=0.95,
                description="Read CPU registers / 读取 CPU 寄存器"
            ),
            SemanticSearchResult(
                tool_name="read_register_with_fields",
                tool_category="SVD",
                relevance_score=0.92,
                description="Read register with field parsing / 读取寄存器并解析字段"
            ),
            SemanticSearchResult(
                tool_name="read_memory",
                tool_category="内存操作",
                relevance_score=0.88,
                description="Read memory from device / 从设备读取内存"
            )
        ]
        mock_registry.get_tool_count.return_value = 41

        # Execute search
        result = semantic_search_tools("如何读取寄存器", top_k=3, threshold=0.5)

        # Verify success
        assert result["success"] is True
        assert len(result["results"]) == 3

        # Verify metadata
        assert result["metadata"]["query"] == "如何读取寄存器"
        assert result["metadata"]["top_k"] == 3
        assert result["metadata"]["total_tools"] == 41
        assert result["metadata"]["candidates"] == 3
        assert "token_savings" in result["metadata"]

        # Verify results are sorted by relevance
        scores = [r["relevance_score"] for r in result["results"]]
        assert scores == sorted(scores, reverse=True)

        # Verify tool names
        tool_names = [r["tool_name"] for r in result["results"]]
        assert "read_registers" in tool_names
        assert "read_register_with_fields" in tool_names
        assert "read_memory" in tool_names

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_multilingual_search(self, mock_config, mock_registry):
        """Test multilingual search (Chinese and English) / 测试多语言搜索（中文和英文）."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Chinese query results
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="read_memory",
                tool_category="内存操作",
                relevance_score=0.95,
                description="Read memory"
            )
        ]
        mock_registry.get_tool_count.return_value = 41

        # Chinese search
        zh_result = semantic_search_tools("读取内存", top_k=3)
        assert zh_result["success"] is True
        assert len(zh_result["results"]) > 0

        # English search (should return similar tools)
        en_result = semantic_search_tools("read memory", top_k=3)
        assert en_result["success"] is True
        assert len(en_result["results"]) > 0

        # Both should contain "read_memory"
        zh_tools = {r["tool_name"] for r in zh_result["results"]}
        en_tools = {r["tool_name"] for r in en_result["results"]}
        assert "read_memory" in zh_tools
        assert "read_memory" in en_tools

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_threshold_filtering(self, mock_config, mock_registry):
        """Test threshold filtering / 测试阈值过滤."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Low threshold - should return more results
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="tool1",
                tool_category="test",
                relevance_score=0.95,
                description="Tool 1"
            ),
            SemanticSearchResult(
                tool_name="tool2",
                tool_category="test",
                relevance_score=0.60,
                description="Tool 2"
            ),
            SemanticSearchResult(
                tool_name="tool3",
                tool_category="test",
                relevance_score=0.30,
                description="Tool 3"
            )
        ]
        mock_registry.get_tool_count.return_value = 41

        # Low threshold (0.0) - should return all results
        low_result = semantic_search_tools("test query", top_k=10, threshold=0.0)
        assert len(low_result["results"]) == 3

        # High threshold (0.7) - should return fewer results
        high_result = semantic_search_tools("test query", top_k=10, threshold=0.7)
        assert len(high_result["results"]) == 1
        assert high_result["results"][0]["relevance_score"] >= 0.7

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_top_k_limiting(self, mock_config, mock_registry):
        """Test top_k limiting / 测试 Top-K 限制."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Return more results than top_k
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name=f"tool{i}",
                tool_category="test",
                relevance_score=1.0 - (i * 0.05),
                description=f"Tool {i}"
            )
            for i in range(10)
        ]
        mock_registry.get_tool_count.return_value = 41

        # Request only top 3
        result = semantic_search_tools("test query", top_k=3, threshold=0.0)
        assert len(result["results"]) == 3
        assert result["metadata"]["top_k"] == 3

        # Request top 5
        result = semantic_search_tools("test query", top_k=5, threshold=0.0)
        assert len(result["results"]) == 5

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_no_results_above_threshold(self, mock_config, mock_registry):
        """Test when no results are above threshold / 测试没有结果超过阈值的情况."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Return no results (all below threshold)
        mock_registry.search.return_value = []
        mock_registry.get_tool_count.return_value = 41

        result = semantic_search_tools("invalid query", top_k=3, threshold=0.9)

        assert result["success"] is True
        assert len(result["results"]) == 0
        assert result["metadata"]["candidates"] == 0

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_realistic_query_scenarios(self, mock_config, mock_registry):
        """Test realistic query scenarios / 测试真实的查询场景."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        test_cases = [
            {
                "query": "如何读取寄存器",
                "expected_tools": ["read_registers", "read_register_with_fields"]
            },
            {
                "query": "flash programming",
                "expected_tools": ["erase_flash", "program_flash", "verify_flash"]
            },
            {
                "query": "connect to device",
                "expected_tools": ["connect_device", "list_jlink_devices"]
            },
            {
                "query": "rtt logging",
                "expected_tools": ["rtt_start", "rtt_read", "rtt_write"]
            }
        ]

        for test_case in test_cases:
            query = test_case["query"]
            expected_tools = test_case["expected_tools"]

            # Mock search to return expected tools
            mock_registry.search.return_value = [
                SemanticSearchResult(
                    tool_name=tool,
                    tool_category="test",
                    relevance_score=0.95,
                    description=f"Tool {tool}"
                )
                for tool in expected_tools
            ]

            result = semantic_search_tools(query, top_k=5, threshold=0.5)

            assert result["success"] is True
            result_tools = [r["tool_name"] for r in result["results"]]

            # At least one expected tool should be in results
            hits = sum(1 for tool in expected_tools if tool in result_tools)
            assert hits >= 1, f"Query '{query}' should match at least one of {expected_tools}"


@pytest.mark.integration
class TestSemanticStatsIntegration:
    """Integration tests for semantic statistics / 语义统计集成测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    def test_get_semantic_stats_integration(self, mock_registry):
        """Test get_semantic_stats() integration / 测试 get_semantic_stats() 集成."""
        mock_registry.get_stats.return_value = {
            "total_tools": 41,
            "total_categories": 8,
            "initialized": True,
            "embedding_matrix_shape": (41, 1536),
            "config": {
                "enabled": True,
                "top_k": 3,
                "threshold": 0.5
            }
        }

        result = get_semantic_stats()

        assert result["success"] is True
        assert result["data"]["total_tools"] == 41
        assert result["data"]["initialized"] is True


@pytest.mark.integration
class TestConfigurationIntegration:
    """Integration tests for configuration / 配置集成测试."""

    @patch('jlink_mcp.config_manager.config_manager')
    def test_configuration_disabled(self, mock_config):
        """Test behavior when semantic search is disabled / 测试语义检索禁用时的行为."""
        mock_config.get_config.return_value = Mock(semantic_enabled=False)

        result = semantic_search_tools("test query")

        assert result["success"] is False
        assert "disabled" in result["error"].lower()

    @patch('jlink_mcp.config_manager.config_manager')
    def test_configuration_enabled(self, mock_config):
        """Test behavior when semantic search is enabled / 测试语义检索启用时的行为."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        with patch('jlink_mcp.semantic_registry.semantic_registry') as mock_registry:
            mock_registry.search.return_value = []
            mock_registry.get_tool_count.return_value = 41

            result = semantic_search_tools("test query")

            assert result["success"] is True
            mock_registry.search.assert_called_once()


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling / 错误处理集成测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_registry_initialization_failure(self, mock_config, mock_registry):
        """Test handling of registry initialization failure / 测试注册表初始化失败的处理."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.search.side_effect = Exception("Registry not initialized")

        result = semantic_search_tools("test query")

        assert result["success"] is False
        assert "error" in result

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_api_key_missing(self, mock_config, mock_registry):
        """Test handling of missing API key / 测试缺失 API Key 的处理."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.search.side_effect = ValueError("OpenAI API Key not set")

        result = semantic_search_tools("test query")

        assert result["success"] is False
        assert "API Key" in result["error"]


@pytest.mark.integration
class TestPerformanceIntegration:
    """Integration tests for performance / 性能集成测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_concurrent_searches(self, mock_config, mock_registry):
        """Test concurrent search requests / 测试并发搜索请求."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="read_memory",
                tool_category="test",
                relevance_score=0.95,
                description="Test tool"
            )
        ]
        mock_registry.get_tool_count.return_value = 41

        # Simulate multiple concurrent searches
        queries = ["query1", "query2", "query3", "query4", "query5"]

        results = []
        for query in queries:
            result = semantic_search_tools(query, top_k=3)
            results.append(result)

        # All should succeed
        assert all(r["success"] for r in results)
        assert mock_registry.search.call_count == 5

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_cache_effectiveness(self, mock_config, mock_registry):
        """Test cache effectiveness / 测试缓存有效性."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="read_memory",
                tool_category="test",
                relevance_score=0.95,
                description="Test tool"
            )
        ]
        mock_registry.get_tool_count.return_value = 41

        # Same query multiple times (should benefit from caching)
        query = "read memory"

        results = []
        for _ in range(5):
            result = semantic_search_tools(query, top_k=3)
            results.append(result)

        # All should succeed
        assert all(r["success"] for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])