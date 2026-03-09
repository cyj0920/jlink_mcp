"""性能测试 - 测试 MCP 服务的性能.

测试目标：
- SVD 延迟加载性能
- 索引查找 O(1) 性能
- 设备名称匹配性能
- 寄存器值解析性能
"""

import pytest
import time
from typing import Tuple

from jlink_mcp.svd_manager import SVDManager
from jlink_mcp.flagchip_patch import FlagchipPatch


# ==================== Fixtures ====================

@pytest.fixture
def svd_manager():
    """创建 SVD 管理器实例（每次测试重置单例）."""
    # 重置单例状态
    SVDManager._instance = None
    SVDManager._initialized = False
    manager = SVDManager()
    yield manager
    # 清理
    manager.clear_cache()


@pytest.fixture
def flagchip_patch():
    """创建 Flagchip 补丁实例（每次测试重置单例）."""
    FlagchipPatch._instance = None
    return FlagchipPatch()


@pytest.fixture
def loaded_svd_manager(svd_manager):
    """创建已加载 SVD 的管理器实例."""
    if svd_manager.device_names:
        device_name = svd_manager.device_names[0]
        svd_manager._ensure_device_loaded(device_name)
    return svd_manager


# ==================== SVD 扫描性能测试 ====================

class TestSVDScanPerformance:
    """测试 SVD 文件扫描性能."""

    def test_svd_scan_performance(self, benchmark):
        """测试扫描 SVD 目录的性能（启动时只扫描，不加载）."""
        def scan_svd_files():
            SVDManager._instance = None
            SVDManager._initialized = False
            return SVDManager()

        manager = benchmark(scan_svd_files)
        assert manager is not None
        assert len(manager.device_names) > 0


# ==================== SVD 延迟加载性能测试 ====================

class TestSVDLoadPerformance:
    """测试 SVD 延迟加载性能."""

    def test_first_device_load(self, svd_manager, benchmark):
        """测试首次加载设备 SVD 的性能."""
        if not svd_manager.device_names:
            pytest.skip("没有可用的 SVD 设备")

        device_name = svd_manager.device_names[0]

        def load_device():
            # 重置以确保是首次加载
            SVDManager._instance = None
            SVDManager._initialized = False
            manager = SVDManager()
            manager._ensure_device_loaded(device_name)
            return manager

        manager = benchmark(load_device)
        assert manager is not None

    def test_cached_device_access(self, loaded_svd_manager, benchmark):
        """测试缓存后的设备访问性能."""
        if not loaded_svd_manager.device_names:
            pytest.skip("没有可用的 SVD 设备")

        device_name = loaded_svd_manager.device_names[0]

        def access_cached():
            return loaded_svd_manager.get_device(device_name)

        device = benchmark(access_cached)
        assert device is not None


# ==================== 外设/寄存器索引查找性能测试 ====================

class TestIndexLookupPerformance:
    """测试索引查找性能."""

    def test_peripheral_lookup_o1(self, loaded_svd_manager, benchmark):
        """测试 O(1) 外设查找性能."""
        device_name = loaded_svd_manager.device_names[0]
        peripherals = loaded_svd_manager.get_peripherals(device_name)

        if not peripherals:
            pytest.skip("没有可用的外设")

        peripheral_name = peripherals[0].name

        def lookup_peripheral():
            return loaded_svd_manager.get_peripheral(device_name, peripheral_name)

        peripheral = benchmark(lookup_peripheral)
        assert peripheral is not None

    def test_register_lookup_o1(self, loaded_svd_manager, benchmark):
        """测试 O(1) 寄存器查找性能."""
        device_name = loaded_svd_manager.device_names[0]
        peripherals = loaded_svd_manager.get_peripherals(device_name)

        if not peripherals or not peripherals[0].registers:
            pytest.skip("没有可用的寄存器")

        peripheral_name = peripherals[0].name
        register_name = peripherals[0].registers[0].name

        def lookup_register():
            return loaded_svd_manager.get_register(device_name, peripheral_name, register_name)

        register = benchmark(lookup_register)
        assert register is not None

    def test_lru_cache_hit(self, loaded_svd_manager, benchmark):
        """测试 LRU 缓存命中性能."""
        device_name = loaded_svd_manager.device_names[0]

        # 预热缓存
        loaded_svd_manager.get_peripherals(device_name)

        def cached_query():
            return loaded_svd_manager.get_peripherals(device_name)

        result = benchmark(cached_query)
        assert len(result) > 0

    def test_all_peripherals_iteration(self, loaded_svd_manager, benchmark):
        """测试遍历所有外设的性能."""
        device_name = loaded_svd_manager.device_names[0]

        def iterate_peripherals():
            peripherals = loaded_svd_manager.get_peripherals(device_name)
            return [p.name for p in peripherals]

        names = benchmark(iterate_peripherals)
        assert len(names) > 0


# ==================== 设备名称匹配性能测试 ====================

class TestDeviceMatchPerformance:
    """测试设备名称匹配性能."""

    def test_exact_match_performance(self, flagchip_patch, benchmark):
        """测试精确匹配性能（O(1) 字典查找）."""
        if not flagchip_patch.device_names:
            pytest.skip("没有可用的设备")

        device_name = flagchip_patch.device_names[0]

        def exact_match():
            return flagchip_patch.match_device_name(device_name)

        result = benchmark(exact_match)
        assert result == device_name

    def test_prefix_match_performance(self, flagchip_patch, benchmark):
        """测试前缀匹配性能."""
        # 使用一个常见的前缀
        partial_name = "FC7300"

        def prefix_match():
            return flagchip_patch.match_device_name(partial_name)

        result = benchmark(prefix_match)
        assert result is not None

    def test_match_cache_hit(self, flagchip_patch, benchmark):
        """测试匹配缓存命中性能."""
        if not flagchip_patch.device_names:
            pytest.skip("没有可用的设备")

        device_name = flagchip_patch.device_names[0]

        # 预热缓存
        flagchip_patch.match_device_name(device_name)

        def cached_match():
            return flagchip_patch.match_device_name(device_name)

        result = benchmark(cached_match)
        assert result == device_name

    def test_find_similar_devices(self, flagchip_patch, benchmark):
        """测试查找相似设备的性能."""
        partial_name = "FC7300"

        def find_similar():
            return flagchip_patch.find_similar_devices(partial_name, limit=5)

        results = benchmark(find_similar)
        assert len(results) > 0


# ==================== 寄存器值解析性能测试 ====================

class TestParseRegisterValuePerformance:
    """测试寄存器值解析性能."""

    def test_parse_simple_field(self, loaded_svd_manager, benchmark):
        """测试简单字段解析性能."""
        device_name = loaded_svd_manager.device_names[0]
        peripherals = loaded_svd_manager.get_peripherals(device_name)

        if not peripherals or not peripherals[0].registers:
            pytest.skip("没有可用的寄存器")

        peripheral_name = peripherals[0].name
        register_name = peripherals[0].registers[0].name

        def parse_value():
            return loaded_svd_manager.parse_register_value(
                device_name, peripheral_name, register_name, 0x12345678
            )

        result = benchmark(parse_value)
        assert result is not None

    def test_parse_complex_register(self, loaded_svd_manager, benchmark):
        """测试复杂寄存器解析性能（多字段）."""
        device_name = loaded_svd_manager.device_names[0]
        peripherals = loaded_svd_manager.get_peripherals(device_name)

        # 找一个字段较多的寄存器
        target_register = None
        target_peripheral = None
        for p in peripherals:
            for r in p.registers:
                if len(r.fields) > 5:
                    target_register = r
                    target_peripheral = p
                    break
            if target_register:
                break

        if not target_register:
            pytest.skip("没有找到复杂寄存器")

        def parse_complex():
            return loaded_svd_manager.parse_register_value(
                device_name, target_peripheral.name, target_register.name, 0xFFFFFFFF
            )

        result = benchmark(parse_complex)
        assert result is not None


# ==================== 端到端性能测试 ====================

class TestEndToEndPerformance:
    """测试端到端操作性能."""

    def test_complete_lookup_flow(self, svd_manager, benchmark):
        """测试完整的查询流程：设备 -> 外设 -> 寄存器."""
        if not svd_manager.device_names:
            pytest.skip("没有可用的 SVD 设备")

        device_name = svd_manager.device_names[0]

        def complete_flow():
            device = svd_manager.get_device(device_name)
            if device and device.peripherals:
                peripheral = svd_manager.get_peripheral(device_name, device.peripherals[0].name)
                if peripheral and peripheral.registers:
                    register = svd_manager.get_register(
                        device_name, peripheral.name, peripheral.registers[0].name
                    )
                    return register
            return None

        result = benchmark(complete_flow)
        assert result is not None

    def test_multiple_device_load(self, benchmark):
        """测试加载多个设备的性能."""
        def load_multiple():
            SVDManager._instance = None
            SVDManager._initialized = False
            manager = SVDManager()

            # 加载前 3 个设备
            for device_name in manager.device_names[:3]:
                manager._ensure_device_loaded(device_name)
            return manager

        manager = benchmark(load_multiple)
        assert manager is not None


# ==================== 性能基准验证 ====================

class TestPerformanceBenchmarks:
    """验证性能是否达到基准要求."""

    def test_svd_scan_under_100ms(self, svd_manager):
        """验证 SVD 扫描在 100ms 内完成."""
        start = time.perf_counter()
        SVDManager._instance = None
        SVDManager._initialized = False
        manager = SVDManager()
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 100, f"SVD 扫描耗时 {elapsed:.2f}ms，超过 100ms 阈值"
        print(f"\nSVD 扫描耗时: {elapsed:.2f}ms")

    def test_peripheral_lookup_under_1ms(self, loaded_svd_manager):
        """验证外设查找在 1ms 内完成."""
        device_name = loaded_svd_manager.device_names[0]
        peripherals = loaded_svd_manager.get_peripherals(device_name)
        peripheral_name = peripherals[0].name

        start = time.perf_counter()
        for _ in range(100):
            loaded_svd_manager.get_peripheral(device_name, peripheral_name)
        elapsed = (time.perf_counter() - start) * 1000

        avg_time = elapsed / 100
        assert avg_time < 1, f"外设查找平均耗时 {avg_time:.4f}ms，超过 1ms 阈值"
        print(f"\n外设查找平均耗时: {avg_time:.4f}ms")

    def test_register_lookup_under_1ms(self, loaded_svd_manager):
        """验证寄存器查找在 1ms 内完成."""
        device_name = loaded_svd_manager.device_names[0]
        peripherals = loaded_svd_manager.get_peripherals(device_name)
        peripheral_name = peripherals[0].name
        register_name = peripherals[0].registers[0].name

        start = time.perf_counter()
        for _ in range(100):
            loaded_svd_manager.get_register(device_name, peripheral_name, register_name)
        elapsed = (time.perf_counter() - start) * 1000

        avg_time = elapsed / 100
        assert avg_time < 1, f"寄存器查找平均耗时 {avg_time:.4f}ms，超过 1ms 阈值"
        print(f"\n寄存器查找平均耗时: {avg_time:.4f}ms")

    def test_device_match_under_1ms(self, flagchip_patch):
        """验证设备匹配在 1ms 内完成."""
        device_name = flagchip_patch.device_names[0]

        start = time.perf_counter()
        for _ in range(100):
            flagchip_patch.match_device_name(device_name)
        elapsed = (time.perf_counter() - start) * 1000

        avg_time = elapsed / 100
        assert avg_time < 1, f"设备匹配平均耗时 {avg_time:.4f}ms，超过 1ms 阈值"
        print(f"\n设备匹配平均耗时: {avg_time:.4f}ms")
