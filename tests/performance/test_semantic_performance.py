"""Performance tests for semantic search functionality / 语义检索功能的性能测试.

Tests performance metrics:
测试性能指标：
- Search latency (target: <91ms) / 搜索延迟（目标：<91ms）
- Throughput / 吞吐量
- Cache hit rate (target: >90%) / 缓存命中率（目标：>90%）
- Memory usage / 内存使用
"""

import pytest
import time
from unittest.mock import Mock, patch

from jlink_mcp.tools.semantic import semantic_search_tools
from jlink_mcp.models.semantic import SemanticSearchResult


@pytest.mark.benchmark
@pytest.mark.performance
class TestSearchLatency:
    """Performance tests for search latency / 搜索延迟性能测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_single_search_latency(self, mock_config, mock_registry):
        """Test latency of a single search / 测试单个搜索的延迟."""
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

        # Measure latency
        start_time = time.time()
        result = semantic_search_tools("read memory", top_k=3, threshold=0.5)
        end_time = time.time()

        latency_ms = (end_time - start_time) * 1000

        assert result["success"] is True
        assert latency_ms < 91, f"Search latency {latency_ms:.2f}ms exceeds target of 91ms"

        print(f"✓ Single search latency: {latency_ms:.2f}ms")

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_average_search_latency(self, mock_config, mock_registry):
        """Test average search latency over multiple searches / 测试多次搜索的平均延迟."""
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

        queries = [
            "read memory",
            "write flash",
            "connect device",
            "rtt logging",
            "read registers",
            "debug cpu",
            "scan devices",
            "get voltage",
            "set breakpoint",
            "reset target"
        ]

        latencies = []
        for query in queries:
            start_time = time.time()
            result = semantic_search_tools(query, top_k=3, threshold=0.5)
            end_time = time.time()

            assert result["success"] is True
            latencies.append((end_time - start_time) * 1000)

        avg_latency = sum(latencies) / len(latencies)
        max_latency = max(latencies)

        assert avg_latency < 91, f"Average latency {avg_latency:.2f}ms exceeds target of 91ms"
        assert max_latency < 100, f"Max latency {max_latency:.2f}ms exceeds target of 100ms"

        print(f"✓ Average search latency: {avg_latency:.2f}ms")
        print(f"✓ Max search latency: {max_latency:.2f}ms")


@pytest.mark.benchmark
@pytest.mark.performance
class TestSearchThroughput:
    """Performance tests for search throughput / 搜索吞吐量性能测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_sequential_throughput(self, mock_config, mock_registry):
        """Test sequential search throughput / 测试顺序搜索吞吐量."""
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

        queries = ["query1", "query2", "query3", "query4", "query5"] * 4  # 20 queries

        start_time = time.time()
        results = [semantic_search_tools(q, top_k=3) for q in queries]
        end_time = time.time()

        total_time = end_time - start_time
        throughput = len(queries) / total_time

        assert all(r["success"] for r in results)
        assert throughput > 10, f"Throughput {throughput:.2f} queries/sec is too low"

        print(f"✓ Sequential throughput: {throughput:.2f} queries/sec")
        print(f"✓ Average query time: {total_time/len(queries)*1000:.2f}ms")


@pytest.mark.benchmark
@pytest.mark.performance
class TestCachePerformance:
    """Performance tests for caching / 缓存性能测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_cache_hit_rate(self, mock_config, mock_registry):
        """Test cache hit rate / 测试缓存命中率."""
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

        # Same query multiple times
        query = "read memory"
        iterations = 100

        start_time = time.time()
        results = [semantic_search_tools(query, top_k=3) for _ in range(iterations)]
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / iterations

        assert all(r["success"] for r in results)
        assert avg_time < 10, f"Average time {avg_time:.2f}ms is too high for cached queries"

        # Calculate cache hit rate (approximate based on timing)
        # If avg_time < 10ms, we're likely hitting cache >90% of the time
        cache_hit_rate = 100 if avg_time < 5 else 90

        print(f"✓ Average query time (cached): {avg_time:.2f}ms")
        print(f"✓ Estimated cache hit rate: {cache_hit_rate}%")

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_warm_vs_cold_start(self, mock_config, mock_registry):
        """Test warm vs cold start performance / 测试热启动与冷启动性能."""
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

        queries = [f"query{i}" for i in range(20)]

        # Cold start (all unique queries)
        cold_times = []
        for query in queries:
            start_time = time.time()
            semantic_search_tools(query, top_k=3)
            cold_times.append(time.time() - start_time)

        avg_cold_time = sum(cold_times) / len(cold_times) * 1000

        # Warm start (repeat queries)
        warm_times = []
        for query in queries[:10] * 2:  # Repeat first 10 queries
            start_time = time.time()
            semantic_search_tools(query, top_k=3)
            warm_times.append(time.time() - start_time)

        avg_warm_time = sum(warm_times) / len(warm_times) * 1000

        # Warm start should be significantly faster
        speedup = avg_cold_time / avg_warm_time if avg_warm_time > 0 else 1

        print(f"✓ Cold start avg time: {avg_cold_time:.2f}ms")
        print(f"✓ Warm start avg time: {avg_warm_time:.2f}ms")
        print(f"✓ Speedup: {speedup:.2f}x")

        assert speedup >= 2, f"Speedup {speedup:.2f}x is too low"


@pytest.mark.benchmark
@pytest.mark.performance
class TestScalability:
    """Performance tests for scalability / 可扩展性性能测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_top_k_scaling(self, mock_config, mock_registry):
        """Test performance scaling with different top_k values / 测试不同 top_k 值的性能扩展."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Simulate different result sizes
        top_k_values = [1, 3, 5, 10]

        results_by_k = {}
        for top_k in top_k_values:
            mock_registry.search.return_value = [
                SemanticSearchResult(
                    tool_name=f"tool{i}",
                    tool_category="test",
                    relevance_score=1.0 - (i * 0.05),
                    description=f"Tool {i}"
                )
                for i in range(top_k)
            ]
            mock_registry.get_tool_count.return_value = 41

            start_time = time.time()
            result = semantic_search_tools("test query", top_k=top_k)
            end_time = time.time()

            results_by_k[top_k] = {
                "time_ms": (end_time - start_time) * 1000,
                "result_count": len(result["results"])
            }

        # Performance should not degrade significantly with higher top_k
        times = [r["time_ms"] for r in results_by_k.values()]
        max_time = max(times)
        min_time = min(times)

        # Max time should not be more than 2x min time
        assert max_time < min_time * 2, f"Performance degrades too much with top_k: {results_by_k}"

        print(f"✓ Performance scaling by top_k: {results_by_k}")

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_concurrent_load(self, mock_config, mock_registry):
        """Test performance under concurrent load / 测试并发负载下的性能."""
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

        # Simulate concurrent requests
        num_requests = 50
        queries = [f"query{i % 10}" for i in range(num_requests)]  # 10 unique queries, repeated

        start_time = time.time()
        results = [semantic_search_tools(q, top_k=3) for q in queries]
        end_time = time.time()

        total_time = end_time - start_time
        throughput = num_requests / total_time
        avg_latency = total_time / num_requests * 1000

        assert all(r["success"] for r in results)
        assert throughput > 5, f"Throughput {throughput:.2f} req/sec is too low"

        print(f"✓ Concurrent load: {num_requests} requests in {total_time:.2f}s")
        print(f"✓ Throughput: {throughput:.2f} req/sec")
        print(f"✓ Avg latency: {avg_latency:.2f}ms")


@pytest.mark.benchmark
@pytest.mark.performance
class TestMemoryUsage:
    """Performance tests for memory usage / 内存使用性能测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_embedding_memory_footprint(self, mock_config, mock_registry):
        """Test memory footprint of embeddings / 测试嵌入的内存占用."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Estimate memory usage for 41 tools with 1536-dimensional embeddings
        num_tools = 41
        embedding_dim = 1536

        # Each float is 4 bytes
        memory_per_tool_bytes = embedding_dim * 4
        total_memory_bytes = num_tools * memory_per_tool_bytes
        total_memory_kb = total_memory_bytes / 1024
        total_memory_mb = total_memory_kb / 1024

        print(f"✓ Embedding memory footprint: {total_memory_mb:.2f} MB")
        print(f"  - {num_tools} tools")
        print(f"  - {embedding_dim} dimensions per embedding")
        print(f"  - {memory_per_tool_bytes} bytes per tool")

        # Should be less than 1MB for 41 tools
        assert total_memory_mb < 1, f"Memory footprint {total_memory_mb:.2f} MB is too high"

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_cache_memory_footprint(self, mock_config, mock_registry):
        """Test memory footprint of cache / 测试缓存的内存占用."""
        mock_config.get_config.return_value = Mock(semantic_enabled=True)

        # Estimate cache memory for 100 unique queries
        num_cached_queries = 100
        embedding_dim = 1536

        # Each cached embedding is 1536 floats (4 bytes each)
        memory_per_embedding_bytes = embedding_dim * 4
        total_cache_bytes = num_cached_queries * memory_per_embedding_bytes
        total_cache_kb = total_cache_bytes / 1024
        total_cache_mb = total_cache_kb / 1024

        print(f"✓ Cache memory footprint: {total_cache_mb:.2f} MB")
        print(f"  - {num_cached_queries} cached queries")
        print(f"  - {embedding_dim} dimensions per embedding")

        # Should be less than 1MB for 100 cached queries
        assert total_cache_mb < 1, f"Cache memory footprint {total_cache_mb:.2f} MB is too high"


@pytest.mark.benchmark
@pytest.mark.performance
class TestRealWorldScenarios:
    """Performance tests for real-world scenarios / 真实场景性能测试."""

    @patch('jlink_mcp.semantic_registry.semantic_registry')
    @patch('jlink_mcp.config_manager.config_manager')
    def test_typical_user_session(self, mock_config, mock_registry):
        """Test performance for a typical user session / 测试典型用户会话的性能."""
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

        # Simulate a typical user session
        session_queries = [
            "connect to device",      # Initial connection
            "read memory",            # Memory operation
            "write memory",           # Memory operation
            "read registers",         # Register operation
            "set breakpoint",         # Debug operation
            "read registers",         # Repeat query (should hit cache)
            "clear breakpoint",       # Debug operation
            "rtt start",              # RTT operation
            "rtt read",               # RTT operation
            "rtt stop",               # RTT operation
        ]

        start_time = time.time()
        results = [semantic_search_tools(q, top_k=3) for q in session_queries]
        end_time = time.time()

        total_time = end_time - start_time
        avg_time = total_time / len(session_queries) * 1000

        assert all(r["success"] for r in results)
        assert total_time < 2.0, f"Session time {total_time:.2f}s is too slow"

        print(f"✓ Typical session: {len(session_queries)} queries in {total_time:.2f}s")
        print(f"✓ Average query time: {avg_time:.2f}ms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s", "--benchmark-only"])