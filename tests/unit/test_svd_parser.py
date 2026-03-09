"""SVD 解析器测试.

测试 SVD 文件解析功能的正确性。
"""

import pytest
from pathlib import Path

from jlink_mcp.svd_manager import SVDManager
from jlink_mcp.models.svd import (
    DeviceSVD, PeripheralInfo, RegisterInfo, FieldInfo,
    CPUInfo, EnumeratedValue
)


# ==================== SVDManager 测试 ====================

class TestSVDManager:
    """测试 SVD 管理器."""

    def test_singleton_pattern(self):
        """测试单例模式."""
        manager1 = SVDManager()
        manager2 = SVDManager()
        assert manager1 is manager2

    def test_is_available(self):
        """测试 SVD 是否可用."""
        manager = SVDManager()
        # 如果 SVD 文件存在，应该返回 True
        assert manager.is_available() == (len(manager.device_names) > 0)

    def test_device_names(self):
        """测试获取设备名称列表."""
        manager = SVDManager()
        names = manager.device_names
        assert isinstance(names, list)
        # 应该至少有一些设备
        if len(names) > 0:
            assert all(isinstance(name, str) for name in names)

    def test_get_device_valid(self):
        """测试获取有效设备."""
        manager = SVDManager()
        names = manager.device_names

        if len(names) > 0:
            device = manager.get_device(names[0])
            assert device is not None
            assert isinstance(device, DeviceSVD)
            assert device.name == names[0]

    def test_get_device_invalid(self):
        """测试获取无效设备."""
        manager = SVDManager()
        device = manager.get_device("InvalidDeviceName")
        assert device is None

    def test_get_peripherals(self):
        """测试获取外设列表."""
        manager = SVDManager()
        names = manager.device_names

        if len(names) > 0:
            peripherals = manager.get_peripherals(names[0])
            assert isinstance(peripherals, list)
            # 检查外设对象
            if len(peripherals) > 0:
                assert isinstance(peripherals[0], PeripheralInfo)

    def test_get_peripheral_valid(self):
        """测试获取有效外设."""
        manager = SVDManager()
        names = manager.device_names

        if len(names) > 0:
            peripherals = manager.get_peripherals(names[0])
            if len(peripherals) > 0:
                peripheral = manager.get_peripheral(names[0], peripherals[0].name)
                assert peripheral is not None
                assert isinstance(peripheral, PeripheralInfo)

    def test_get_peripheral_invalid(self):
        """测试获取无效外设."""
        manager = SVDManager()
        names = manager.device_names

        if len(names) > 0:
            peripheral = manager.get_peripheral(names[0], "InvalidPeripheral")
            assert peripheral is None

    def test_get_register_valid(self):
        """测试获取有效寄存器."""
        manager = SVDManager()
        names = manager.device_names

        if len(names) > 0:
            peripherals = manager.get_peripherals(names[0])
            if len(peripherals) > 0:
                reg_name = peripherals[0].registers[0].name if peripherals[0].registers else None
                if reg_name:
                    register = manager.get_register(
                        names[0],
                        peripherals[0].name,
                        reg_name
                    )
                    assert register is not None
                    assert isinstance(register, RegisterInfo)

    def test_get_register_invalid(self):
        """测试获取无效寄存器."""
        manager = SVDManager()
        names = manager.device_names

        if len(names) > 0:
            peripherals = manager.get_peripherals(names[0])
            if len(peripherals) > 0:
                register = manager.get_register(
                    names[0],
                    peripherals[0].name,
                    "InvalidRegister"
                )
                assert register is None


# ==================== 寄存器值解析测试 ====================

class TestParseRegisterValue:
    """测试寄存器值解析."""

    @pytest.fixture
    def sample_device_data(self):
        """创建示例设备数据."""
        cpu = CPUInfo(
            name="CM7",
            revision="r0p1",
            endian="little",
            mpu_present=True,
            fpu_present=True,
            nvic_prio_bits=4
        )

        # 创建带枚举值的字段
        field1 = FieldInfo(
            name="ENABLE",
            description="Enable field",
            bit_offset=0,
            bit_width=1,
            access="read-write",
            enumerated_values=[
                EnumeratedValue(name="Disabled", value=0, description="Feature disabled"),
                EnumeratedValue(name="Enabled", value=1, description="Feature enabled")
            ]
        )

        # 创建不带枚举值的字段
        field2 = FieldInfo(
            name="MODE",
            description="Mode field",
            bit_offset=1,
            bit_width=2,
            access="read-write"
        )

        # 创建多字段
        field3 = FieldInfo(
            name="STATUS",
            description="Status field",
            bit_offset=8,
            bit_width=4,
            access="read-only"
        )

        register = RegisterInfo(
            name="CTRL",
            description="Control register",
            address_offset=0x0,
            size=32,
            access="read-write",
            reset_value=0x0,
            fields=[field1, field2, field3]
        )

        peripheral = PeripheralInfo(
            name="TEST",
            description="Test peripheral",
            group_name="TEST",
            base_address=0x40000000,
            registers=[register]
        )

        device = DeviceSVD(
            name="TestDevice",
            vendor="TestVendor",
            version="1.0",
            cpu=cpu,
            peripherals=[peripheral]
        )

        return {
            "device": device,
            "peripheral": peripheral,
            "register": register
        }

    def test_parse_value_zero(self, sample_device_data):
        """测试解析值为 0."""
        manager = SVDManager()
        # 添加测试数据
        manager._devices["TestDevice"] = sample_device_data["device"]

        result = manager.parse_register_value(
            "TestDevice",
            "TEST",
            "CTRL",
            0x0
        )

        assert result is not None
        assert result["raw_value"] == 0
        assert result["hex_value"] == "0x0"
        assert len(result["fields"]) == 3

        # 检查第一个字段（ENABLE）的值
        enable_field = result["fields"][0]
        assert enable_field["field_value"] == 0
        assert enable_field["enum_name"] == "Disabled"

    def test_parse_value_with_enum(self, sample_device_data):
        """测试带枚举值的解析."""
        manager = SVDManager()
        manager._devices["TestDevice"] = sample_device_data["device"]

        # ENABLE = 1, MODE = 2
        result = manager.parse_register_value(
            "TestDevice",
            "TEST",
            "CTRL",
            0x3
        )

        assert result is not None
        enable_field = result["fields"][0]
        assert enable_field["field_value"] == 1
        assert enable_field["enum_name"] == "Enabled"

    def test_parse_value_without_enum(self, sample_device_data):
        """测试不带枚举值的解析."""
        manager = SVDManager()
        manager._devices["TestDevice"] = sample_device_data["device"]

        # MODE = 3 (位 1-2)
        result = manager.parse_register_value(
            "TestDevice",
            "TEST",
            "CTRL",
            0x6
        )

        assert result is not None
        mode_field = result["fields"][1]
        assert mode_field["field_value"] == 3
        assert mode_field["enum_name"] is None

    def test_parse_value_multiple_fields(self, sample_device_data):
        """测试多字段解析."""
        manager = SVDManager()
        manager._devices["TestDevice"] = sample_device_data["device"]

        # ENABLE=1 (bit 0), MODE=2 (bits 1-2 = 10b), STATUS=10 (bits 8-11 = 1010b)
        # 值 = 1010_0000_0101b = 0xA05
        result = manager.parse_register_value(
            "TestDevice",
            "TEST",
            "CTRL",
            0xA05
        )

        assert result is not None
        assert len(result["fields"]) == 3

        # 检查各字段值
        enable_field = result["fields"][0]
        mode_field = result["fields"][1]
        status_field = result["fields"][2]

        assert enable_field["field_value"] == 1
        assert mode_field["field_value"] == 2
        assert status_field["field_value"] == 10

    def test_parse_value_32bit(self, sample_device_data):
        """测试 32 位值解析."""
        manager = SVDManager()
        manager._devices["TestDevice"] = sample_device_data["device"]

        result = manager.parse_register_value(
            "TestDevice",
            "TEST",
            "CTRL",
            0x12345678
        )

        assert result is not None
        assert result["raw_value"] == 0x12345678
        assert result["hex_value"] == "0x12345678"

    def test_parse_invalid_register(self, sample_device_data):
        """测试解析无效寄存器."""
        manager = SVDManager()
        manager._devices["TestDevice"] = sample_device_data["device"]

        result = manager.parse_register_value(
            "TestDevice",
            "TEST",
            "InvalidRegister",
            0x12345678
        )

        assert result is None


# ==================== SVD 文件结构测试 ====================

class TestSVDFileStructure:
    """测试 SVD 文件结构."""

    def test_svd_file_exists(self):
        """测试 SVD 文件是否存在."""
        svd_path = Path(__file__).parent.parent.parent / "SVD_V1.5.6"
        if svd_path.exists():
            svd_files = list(svd_path.glob("*.svd"))
            assert len(svd_files) > 0

    def test_svd_file_names(self):
        """测试 SVD 文件命名."""
        svd_path = Path(__file__).parent.parent.parent / "SVD_V1.5.6"
        if svd_path.exists():
            svd_files = list(svd_path.glob("*.svd"))
            for svd_file in svd_files:
                # 检查文件名格式
                assert svd_file.suffix == ".svd"
                assert len(svd_file.stem) > 0


# ==================== 性能测试 ====================

class TestSVDPerformance:
    """测试 SVD 性能."""

    def test_load_performance(self, benchmark):
        """测试加载性能."""
        def load_svd():
            return SVDManager()

        # 使用 pytest-benchmark 测量加载时间
        manager = benchmark(load_svd)
        assert manager is not None

    def test_query_performance(self, benchmark):
        """测试查询性能."""
        manager = SVDManager()

        if len(manager.device_names) > 0:
            def query_device():
                return manager.get_device(manager.device_names[0])

            device = benchmark(query_device)
            assert device is not None


# ==================== 边界测试 ====================

class TestSVDBoundaryConditions:
    """测试 SVD 边界条件."""

    def test_empty_fields(self):
        """测试空字段列表."""
        register = RegisterInfo(
            name="NoFields",
            description="Register without fields",
            address_offset=0x0,
            size=32,
            access="read-write",
            reset_value=0,
            fields=[]
        )

        assert len(register.fields) == 0

    def test_32_bit_field(self):
        """测试 32 位字段."""
        field = FieldInfo(
            name="Full32",
            description="32-bit field",
            bit_offset=0,
            bit_width=32,
            access="read-write"
        )

        assert field.bit_width == 32

    def test_multiple_enums(self):
        """测试多个枚举值."""
        enums = [
            EnumeratedValue(name="Mode0", value=0, description="Mode 0"),
            EnumeratedValue(name="Mode1", value=1, description="Mode 1"),
            EnumeratedValue(name="Mode2", value=2, description="Mode 2"),
            EnumeratedValue(name="Mode3", value=3, description="Mode 3"),
        ]

        assert len(enums) == 4
        assert all(e.value in [0, 1, 2, 3] for e in enums)