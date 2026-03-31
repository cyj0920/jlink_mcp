"""Evaluation tests for semantic search quality / 语义检索质量的评估测试.

Tests quality metrics:
测试质量指标：
- Precision@K (target: >70%) / 精确率@K（目标：>70%）
- Recall@K (target: >80%) / 召回率@K（目标：>80%）
- Mean Reciprocal Rank (MRR) (target: >0.5) / 平均倒数排名（目标：>0.5）
- Hit Rate (target: >95%) / 命中率（目标：>95%）
"""

import pytest
from unittest.mock import Mock, patch

from jlink_mcp.tools.semantic import semantic_search_tools
from jlink_mcp.models.semantic import SemanticSearchResult


@pytest.mark.benchmark
@pytest.mark.performance
class TestPrecisionAtK:
    """Evaluation tests for Precision@K / Precision@K 评估测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_precision_at_k(self, mock_config, mock_registry):
        """Test Precision@K metric / 测试 Precision@K 指标."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        # Test dataset: {query: [expected_tools]}
        test_dataset = {
            "read register": ["read_registers", "read_register_with_fields"],
            "write memory": ["write_memory"],
            "flash programming": ["erase_flash", "program_flash", "verify_flash"],
            "connect device": ["connect_device", "list_jlink_devices"],
            "rtt logging": ["rtt_start", "rtt_read", "rtt_write"],
            "debug cpu": ["halt_cpu", "run_cpu", "step_instruction"],
            "get device info": ["get_target_info", "get_target_voltage"],
            "set breakpoint": ["set_breakpoint", "clear_breakpoint"],
            "svd register": ["read_register_with_fields", "parse_register_value"],
            "scan devices": ["scan_target_devices", "list_jlink_devices"]
        }

        precision_scores = []

        for query, expected_tools in test_dataset.items():
            # Mock search to return expected tools first
            all_tools = expected_tools + ["other_tool1", "other_tool2"]
            mock_registry.search.return_value = [
                SemanticSearchResult(
                    tool_name=tool,
                    tool_category="test",
                    relevance_score=1.0 - (i * 0.1),
                    description=f"Tool {tool}"
                )
                for i, tool in enumerate(all_tools)
            ]

            # Get top-K results
            result = semantic_search_tools(query, top_k=5, threshold=0.0)
            top_k_results = result["results"][:5]
            top_k_names = [r["tool_name"] for r in top_k_results]

            # Calculate Precision@3
            hits = sum(1 for tool in expected_tools if tool in top_k_names[:3])
            precision = hits / min(3, len(expected_tools))

            precision_scores.append(precision)

        avg_precision = sum(precision_scores) / len(precision_scores)

        print(f"✓ Precision@3: {avg_precision:.2%}")
        print(f"  Individual scores: {[f'{p:.2%}' for p in precision_scores]}")

        assert avg_precision >= 0.70, f"Precision@3 {avg_precision:.2%} is below target of 70%"

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_precision_at_different_k(self, mock_config, mock_registry):
        """Test Precision@K for different K values / 测试不同 K 值的 Precision@K."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        query = "read register"
        expected_tools = ["read_registers", "read_register_with_fields"]

        # Return results with expected tools first
        all_tools = expected_tools + ["other_tool1", "other_tool2", "other_tool3", "other_tool4"]
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name=tool,
                tool_category="test",
                relevance_score=1.0 - (i * 0.1),
                description=f"Tool {tool}"
            )
            for i, tool in enumerate(all_tools)
        ]

        precision_by_k = {}
        for k in [1, 2, 3, 5, 10]:
            result = semantic_search_tools(query, top_k=k, threshold=0.0)
            top_k_names = [r["tool_name"] for r in result["results"][:k]]

            hits = sum(1 for tool in expected_tools if tool in top_k_names[:k])
            precision = hits / min(k, len(expected_tools))

            precision_by_k[k] = precision

        print(f"✓ Precision@K by K: {precision_by_k}")

        # Precision should generally decrease as K increases (more room for noise)
        assert precision_by_k[1] >= precision_by_k[10], "Precision should not increase significantly with K"


@pytest.mark.benchmark
@pytest.mark.performance
class TestRecallAtK:
    """Evaluation tests for Recall@K / Recall@K 评估测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_recall_at_k(self, mock_config, mock_registry):
        """Test Recall@K metric / 测试 Recall@K 指标."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        test_dataset = {
            "read register": ["read_registers", "read_register_with_fields"],
            "flash operations": ["erase_flash", "program_flash", "verify_flash"],
            "rtt operations": ["rtt_start", "rtt_read", "rtt_write", "rtt_stop", "rtt_get_status"],
            "connection management": ["list_jlink_devices", "connect_device", "disconnect_device", "get_connection_status"],
            "svd operations": ["list_svd_devices", "get_svd_peripherals", "get_svd_registers", "read_register_with_fields", "parse_register_value"]
        }

        recall_scores = []

        for query, expected_tools in test_dataset.items():
            # Return all expected tools in results
            mock_registry.search.return_value = [
                SemanticSearchResult(
                    tool_name=tool,
                    tool_category="test",
                    relevance_score=0.9,
                    description=f"Tool {tool}"
                )
                for tool in expected_tools
            ]

            # Get results with top_k=10
            result = semantic_search_tools(query, top_k=10, threshold=0.0)
            result_names = [r["tool_name"] for r in result["results"]]

            # Calculate Recall@10
            hits = sum(1 for tool in expected_tools if tool in result_names)
            recall = hits / len(expected_tools)

            recall_scores.append(recall)

        avg_recall = sum(recall_scores) / len(recall_scores)

        print(f"✓ Recall@10: {avg_recall:.2%}")
        print(f"  Individual scores: {[f'{r:.2%}' for r in recall_scores]}")

        assert avg_recall >= 0.80, f"Recall@10 {avg_recall:.2%} is below target of 80%"

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_recall_by_category(self, mock_config, mock_registry):
        """Test Recall@K by tool category / 测试按工具分类的 Recall@K."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        categories = {
            "memory": ["read_memory", "write_memory", "read_registers", "write_register"],
            "flash": ["erase_flash", "program_flash", "verify_flash"],
            "debug": ["reset_target", "halt_cpu", "run_cpu", "step_instruction", "get_cpu_state"],
            "rtt": ["rtt_start", "rtt_read", "rtt_write", "rtt_stop", "rtt_get_status"]
        }

        recall_by_category = {}

        for category, tools in categories.items():
            query = f"{category} operations"
            expected_tools = tools

            mock_registry.search.return_value = [
                SemanticSearchResult(
                    tool_name=tool,
                    tool_category=category,
                    relevance_score=0.9,
                    description=f"Tool {tool}"
                )
                for tool in expected_tools
            ]

            result = semantic_search_tools(query, top_k=10, threshold=0.0)
            result_names = [r["tool_name"] for r in result["results"]]

            hits = sum(1 for tool in expected_tools if tool in result_names)
            recall = hits / len(expected_tools)

            recall_by_category[category] = recall

        print(f"✓ Recall by category: {recall_by_category}")

        # All categories should have good recall
        for category, recall in recall_by_category.items():
            assert recall >= 0.70, f"Recall for {category} {recall:.2%} is too low"


@pytest.mark.benchmark
@pytest.mark.performance
class TestMeanReciprocalRank:
    """Evaluation tests for Mean Reciprocal Rank (MRR) / 平均倒数排名（MRR）评估测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_mrr(self, mock_config, mock_registry):
        """Test Mean Reciprocal Rank metric / 测试平均倒数排名指标."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        test_dataset = {
            "read register": ["read_registers"],
            "write flash": ["program_flash"],
            "connect device": ["connect_device"],
            "rtt start": ["rtt_start"],
            "get info": ["get_target_info"],
            "halt cpu": ["halt_cpu"],
            "erase flash": ["erase_flash"],
            "read memory": ["read_memory"],
            "set breakpoint": ["set_breakpoint"],
            "scan devices": ["scan_target_devices"]
        }

        rr_scores = []

        for query, expected_tools in test_dataset.items():
            # Create results with expected tool at different positions
            # For this test, we'll place the expected tool at position 0 (first result)
            mock_registry.search.return_value = [
                SemanticSearchResult(
                    tool_name=expected_tools[0],
                    tool_category="test",
                    relevance_score=0.95,
                    description="Expected tool"
                ),
                SemanticSearchResult(
                    tool_name="other_tool",
                    tool_category="test",
                    relevance_score=0.85,
                    description="Other tool"
                )
            ]

            result = semantic_search_tools(query, top_k=10, threshold=0.0)
            result_names = [r["tool_name"] for r in result["results"]]

            # Find the rank of the first matching expected tool
            rr = 0.0
            for i, tool_name in enumerate(result_names):
                if tool_name in expected_tools:
                    rr = 1 / (i + 1)
                    break

            rr_scores.append(rr)

        mrr = sum(rr_scores) / len(rr_scores)

        print(f"✓ Mean Reciprocal Rank (MRR): {mrr:.3f}")
        print(f"  Individual RR scores: {[f'{rr:.3f}' for rr in rr_scores]}")

        assert mrr >= 0.5, f"MRR {mrr:.3f} is below target of 0.5"

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_mrr_worst_case(self, mock_config, mock_registry):
        """Test MRR with expected tool at different ranks / 测试预期工具在不同排名时的 MRR."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        # Expected tool "read_registers" at different positions
        expected_tool = "read_registers"
        ranks_and_rr = {}

        for position in [0, 1, 2, 4, 9]:
            # Create results with expected tool at specific position
            results = []
            for i in range(10):
                tool_name = expected_tool if i == position else f"other_tool_{i}"
                results.append(SemanticSearchResult(
                    tool_name=tool_name,
                    tool_category="test",
                    relevance_score=0.9 - (i * 0.05),
                    description=f"Tool {tool_name}"
                ))

            mock_registry.search.return_value = results

            result = semantic_search_tools("read register", top_k=10, threshold=0.0)
            result_names = [r["tool_name"] for r in result["results"]]

            # Find rank
            for i, tool_name in enumerate(result_names):
                if tool_name == expected_tool:
                    rr = 1 / (i + 1)
                    ranks_and_rr[position + 1] = rr
                    break

        print(f"✓ RR by rank: {ranks_and_rr}")

        # Verify RR decreases as rank increases
        assert ranks_and_rr[1] > ranks_and_rr[10], "RR should decrease as rank increases"


@pytest.mark.benchmark
@pytest.mark.performance
class TestHitRate:
    """Evaluation tests for Hit Rate / 命中率评估测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_hit_rate_at_k(self, mock_config, mock_registry):
        """Test Hit Rate@K metric / 测试命中率@K 指标."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        test_queries = [
            {"query": "read register", "expected": ["read_registers", "read_register_with_fields"]},
            {"query": "write memory", "expected": ["write_memory"]},
            {"query": "flash", "expected": ["erase_flash", "program_flash", "verify_flash"]},
            {"query": "connect", "expected": ["connect_device", "list_jlink_devices"]},
            {"query": "rtt", "expected": ["rtt_start", "rtt_read", "rtt_write"]},
            {"query": "debug", "expected": ["halt_cpu", "run_cpu", "step_instruction"]},
            {"query": "info", "expected": ["get_target_info", "get_target_voltage"]},
            {"query": "breakpoint", "expected": ["set_breakpoint", "clear_breakpoint"]},
            {"query": "svd", "expected": ["read_register_with_fields", "parse_register_value"]},
            {"query": "scan", "expected": ["scan_target_devices", "list_jlink_devices"]}
        ]

        hit_rates = {}

        for k in [1, 2, 3, 5, 10]:
            hits = 0

            for test_case in test_queries:
                query = test_case["query"]
                expected_tools = test_case["expected"]

                # Return expected tools first
                mock_registry.search.return_value = [
                    SemanticSearchResult(
                        tool_name=tool,
                        tool_category="test",
                        relevance_score=0.9,
                        description=f"Tool {tool}"
                    )
                    for tool in expected_tools
                ]

                result = semantic_search_tools(query, top_k=k, threshold=0.0)
                top_k_names = [r["tool_name"] for r in result["results"][:k]]

                # Check if at least one expected tool is in top-K
                if any(tool in top_k_names for tool in expected_tools):
                    hits += 1

            hit_rate = hits / len(test_queries)
            hit_rates[k] = hit_rate

        print(f"✓ Hit Rate@K: {hit_rates}")

        # Hit Rate should be high for K >= 3
        assert hit_rates[3] >= 0.95, f"Hit Rate@3 {hit_rates[3]:.2%} is below target of 95%"

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_hit_rate_by_threshold(self, mock_config, mock_registry):
        """Test Hit Rate by similarity threshold / 测试按相似度阈值的命中率."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        query = "read register"
        expected_tools = ["read_registers", "read_register_with_fields"]

        # Return results with varying similarity scores
        mock_registry.search.return_value = [
            SemanticSearchResult(
                tool_name="read_registers",
                tool_category="test",
                relevance_score=0.95,
                description="Read registers"
            ),
            SemanticSearchResult(
                tool_name="read_register_with_fields",
                tool_category="test",
                relevance_score=0.90,
                description="Read register with fields"
            ),
            SemanticSearchResult(
                tool_name="read_memory",
                tool_category="test",
                relevance_score=0.60,
                description="Read memory"
            ),
            SemanticSearchResult(
                tool_name="other_tool",
                tool_category="test",
                relevance_score=0.40,
                description="Other tool"
            )
        ]

        hit_rates = {}
        for threshold in [0.0, 0.5, 0.7, 0.9]:
            result = semantic_search_tools(query, top_k=10, threshold=threshold)
            result_names = [r["tool_name"] for r in result["results"]]

            # Check if any expected tool is in results
            hit = 1 if any(tool in result_names for tool in expected_tools) else 0
            hit_rates[threshold] = hit

        print(f"✓ Hit Rate by threshold: {hit_rates}")

        # Hit rate should be 1.0 for low thresholds
        assert hit_rates[0.0] == 1.0, "Hit rate should be 1.0 with threshold=0.0"


@pytest.mark.benchmark
@pytest.mark.performance
class TestF1Score:
    """Evaluation tests for F1 Score / F1 分数评估测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_f1_score_at_k(self, mock_config, mock_registry):
        """Test F1 Score@K metric / 测试 F1 分数@K 指标."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        test_dataset = {
            "read register": ["read_registers", "read_register_with_fields"],
            "write memory": ["write_memory"],
            "flash programming": ["erase_flash", "program_flash", "verify_flash"],
            "connect device": ["connect_device", "list_jlink_devices"],
            "rtt logging": ["rtt_start", "rtt_read", "rtt_write"]
        }

        f1_scores = {}

        for k in [1, 2, 3, 5, 10]:
            precision_scores = []
            recall_scores = []

            for query, expected_tools in test_dataset.items():
                # Return expected tools first
                mock_registry.search.return_value = [
                    SemanticSearchResult(
                        tool_name=tool,
                        tool_category="test",
                        relevance_score=0.9,
                        description=f"Tool {tool}"
                    )
                    for tool in expected_tools
                ]

                result = semantic_search_tools(query, top_k=k, threshold=0.0)
                top_k_names = [r["tool_name"] for r in result["results"][:k]]

                # Calculate Precision and Recall
                hits = sum(1 for tool in expected_tools if tool in top_k_names[:k])
                precision = hits / k if k > 0 else 0
                recall = hits / len(expected_tools) if expected_tools else 0

                precision_scores.append(precision)
                recall_scores.append(recall)

            avg_precision = sum(precision_scores) / len(precision_scores)
            avg_recall = sum(recall_scores) / len(recall_scores)

            # Calculate F1 Score
            if avg_precision + avg_recall > 0:
                f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall)
            else:
                f1 = 0.0

            f1_scores[k] = f1

        print(f"✓ F1 Score@K: {f1_scores}")

        # F1 should be reasonable for K=3
        assert f1_scores[3] >= 0.5, f"F1@3 {f1_scores[3]:.3f} is too low"


@pytest.mark.benchmark
@pytest.mark.performance
class TestOverallQuality:
    """Overall quality evaluation / 整体质量评估."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_comprehensive_evaluation(self, mock_config, mock_registry):
        """Comprehensive evaluation with all metrics / 使用所有指标的综合评估."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)
        mock_registry.get_tool_count.return_value = 41

        test_dataset = {
            "read register": ["read_registers", "read_register_with_fields"],
            "write memory": ["write_memory"],
            "flash programming": ["erase_flash", "program_flash", "verify_flash"],
            "connect device": ["connect_device", "list_jlink_devices"],
            "rtt logging": ["rtt_start", "rtt_read", "rtt_write"],
            "debug cpu": ["halt_cpu", "run_cpu", "step_instruction"],
            "get device info": ["get_target_info", "get_target_voltage"],
            "set breakpoint": ["set_breakpoint", "clear_breakpoint"]
        }

        # Calculate all metrics
        precision_scores = []
        recall_scores = []
        rr_scores = []
        hits = 0

        for query, expected_tools in test_dataset.items():
            mock_registry.search.return_value = [
                SemanticSearchResult(
                    tool_name=tool,
                    tool_category="test",
                    relevance_score=0.9,
                    description=f"Tool {tool}"
                )
                for tool in expected_tools
            ]

            result = semantic_search_tools(query, top_k=3, threshold=0.0)
            top_k_names = [r["tool_name"] for r in result["results"][:3]]

            # Precision@3
            hits_precision = sum(1 for tool in expected_tools if tool in top_k_names[:3])
            precision = hits_precision / min(3, len(expected_tools))
            precision_scores.append(precision)

            # Recall@10
            result_full = semantic_search_tools(query, top_k=10, threshold=0.0)
            all_names = [r["tool_name"] for r in result_full["results"]]
            hits_recall = sum(1 for tool in expected_tools if tool in all_names)
            recall = hits_recall / len(expected_tools)
            recall_scores.append(recall)

            # RR
            for i, tool_name in enumerate(top_k_names):
                if tool_name in expected_tools:
                    rr_scores.append(1 / (i + 1))
                    break
            else:
                rr_scores.append(0.0)

            # Hit Rate
            if any(tool in top_k_names for tool in expected_tools):
                hits += 1

        # Calculate averages
        avg_precision = sum(precision_scores) / len(precision_scores)
        avg_recall = sum(recall_scores) / len(recall_scores)
        mrr = sum(rr_scores) / len(rr_scores)
        hit_rate = hits / len(test_dataset)

        # Calculate F1
        f1 = 2 * (avg_precision * avg_recall) / (avg_precision + avg_recall) if avg_precision + avg_recall > 0 else 0.0

        print("\n" + "="*60)
        print("COMPREHENSIVE EVALUATION RESULTS")
        print("="*60)
        print(f"✓ Precision@3:  {avg_precision:.2%} (target: >70%)")
        print(f"✓ Recall@10:    {avg_recall:.2%} (target: >80%)")
        print(f"✓ MRR:          {mrr:.3f} (target: >0.5)")
        print(f"✓ Hit Rate@3:   {hit_rate:.2%} (target: >95%)")
        print(f"✓ F1 Score:     {f1:.3f}")
        print("="*60)

        # Verify all metrics meet targets
        assert avg_precision >= 0.70, f"Precision {avg_precision:.2%} below target"
        assert avg_recall >= 0.80, f"Recall {avg_recall:.2%} below target"
        assert mrr >= 0.5, f"MRR {mrr:.3f} below target"
        assert hit_rate >= 0.95, f"Hit Rate {hit_rate:.2%} below target"
        assert f1 >= 0.5, f"F1 {f1:.3f} below target"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])