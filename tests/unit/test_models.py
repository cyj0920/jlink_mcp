"""模型验证测试.

测试 Pydantic 数据模型的正确性和边界条件。
"""

import pytest
from pydantic import ValidationError

from jlink_mcp.models.base import (
    OperationStatus,
    MCPError,
    MCPResponse,
    ProgressInfo,
    PaginatedResult
)

from jlink_mcp.models.device import (
    TargetInterface,
    DeviceInfo,
    ConnectionMode,
    ConnectionStatus,
    TargetDeviceInfo
)

from jlink_mcp.models.operations import (
    MemoryReadRequest,
    MemoryWriteRequest,
    RegisterReadResult
)

from jlink_mcp.models.svd import (
    EnumeratedValue,
    FieldInfo,
    RegisterInfo,
    PeripheralInfo,
    CPUInfo,
    DeviceSVD,
    RegisterFieldResult,
    RegisterReadWithFieldsResult
)


# ==================== Base Models ====================

class TestOperationStatus:
    """测试 OperationStatus 枚举."""

    def test_status_values(self):
        """测试状态值."""
        assert OperationStatus.SUCCESS == "success"
        assert OperationStatus.ERROR == "error"
        assert OperationStatus.WARNING == "warning"
        assert OperationStatus.PENDING == "pending"


class TestMCPError:
    """测试 MCPError 模型."""

    def test_create_error(self):
        """测试创建错误."""
        error = MCPError(
            code=1,
            description="Test error",
            suggestion="Test suggestion",
            detail="Test detail"
        )
        assert error.code == 1
        assert error.description == "Test error"
        assert error.suggestion == "Test suggestion"
        assert error.detail == "Test detail"

    def test_create_error_without_detail(self):
        """测试创建不带详情的错误."""
        error = MCPError(
            code=1,
            description="Test error",
            suggestion="Test suggestion"
        )
        assert error.detail is None


class TestMCPResponse:
    """测试 MCPResponse 模型."""

    def test_create_success_response(self):
        """测试创建成功响应."""
        response = MCPResponse.success(
            data={"key": "value"},
            message="Success"
        )
        assert response.status == OperationStatus.SUCCESS
        assert response.data == {"key": "value"}
        assert response.message == "Success"
        assert response.error is None

    def test_create_error_response(self):
        """测试创建错误响应."""
        response = MCPResponse.create_error(
            error_code=1,
            description="Test error",
            suggestion="Test suggestion"
        )
        assert response.status == OperationStatus.ERROR
        assert response.message == "Test error"
        assert response.error is not None
        assert response.error.code == 1

    def test_create_warning_response(self):
        """测试创建警告响应."""
        response = MCPResponse.warning(
            data={"key": "value"},
            message="Warning"
        )
        assert response.status == OperationStatus.WARNING
        assert response.data == {"key": "value"}
        assert response.message == "Warning"


class TestProgressInfo:
    """测试 ProgressInfo 模型."""

    def test_create_progress(self):
        """测试创建进度信息."""
        progress = ProgressInfo(
            current=5,
            total=10,
            percentage=50.0,
            message="Processing"
        )
        assert progress.current == 5
        assert progress.total == 10
        assert progress.percentage == 50.0
        assert progress.message == "Processing"

    def test_is_complete(self):
        """测试是否完成."""
        progress_complete = ProgressInfo(current=10, total=10, percentage=100.0)
        progress_incomplete = ProgressInfo(current=5, total=10, percentage=50.0)

        assert progress_complete.is_complete is True
        assert progress_incomplete.is_complete is False


class TestPaginatedResult:
    """测试 PaginatedResult 模型."""

    def test_create_paginated_result(self):
        """测试创建分页结果."""
        result = PaginatedResult(
            items=["item1", "item2", "item3"],
            total=30,
            page=1,
            page_size=10
        )
        assert result.items == ["item1", "item2", "item3"]
        assert result.total == 30
        assert result.page == 1
        assert result.page_size == 10

    def test_total_pages(self):
        """测试总页数."""
        result = PaginatedResult(
            items=list(range(10)),
            total=25,
            page=1,
            page_size=10
        )
        assert result.total_pages == 3

    def test_has_next(self):
        """测试是否有下一页."""
        result_has_next = PaginatedResult(
            items=list(range(10)),
            total=25,
            page=1,
            page_size=10
        )
        result_no_next = PaginatedResult(
            items=list(range(5)),
            total=5,
            page=1,
            page_size=10
        )

        assert result_has_next.has_next is True
        assert result_no_next.has_next is False

    def test_has_prev(self):
        """测试是否有上一页."""
        result_has_prev = PaginatedResult(
            items=list(range(10)),
            total=25,
            page=2,
            page_size=10
        )
        result_no_prev = PaginatedResult(
            items=list(range(10)),
            total=25,
            page=1,
            page_size=10
        )

        assert result_has_prev.has_prev is True
        assert result_no_prev.has_prev is False


# ==================== Device Models ====================

class TestTargetInterface:
    """测试 TargetInterface 枚举."""

    def test_interface_values(self):
        """测试接口值."""
        assert TargetInterface.JTAG == "JTAG"
        assert TargetInterface.SWD == "SWD"


class TestDeviceInfo:
    """测试 DeviceInfo 模型."""

    def test_create_device_info(self):
        """测试创建设备信息."""
        device = DeviceInfo(
            serial_number="941000024",
            product_name="J-Link",
            firmware_version="V11.0.0",
            connection_type="USB",
            hardware_version="V11.0"
        )
        assert device.serial_number == "941000024"
        assert device.product_name == "J-Link"
        assert device.firmware_version == "V11.0.0"


class TestConnectionStatus:
    """测试 ConnectionStatus 模型."""

    def test_create_connected_status(self):
        """测试创建已连接状态."""
        status = ConnectionStatus(
            connected=True,
            device_serial="941000024",
            target_interface=TargetInterface.JTAG,
            target_voltage=3.3,
            target_connected=True,
            firmware_version="V11.0.0",
            connection_mode=ConnectionMode.PRIVATE,
            connection_strategy="patch_match:Flagchip",
            requested_chip_name="FC7300F4MDD",
            connected_chip_name="FC7300F4MDDxXxxxT1C"
        )
        assert status.connected is True
        assert status.device_serial == "941000024"
        assert status.target_interface == TargetInterface.JTAG
        assert status.target_voltage == 3.3
        assert status.connection_mode == ConnectionMode.PRIVATE
        assert status.connected_chip_name == "FC7300F4MDDxXxxxT1C"


class TestTargetDeviceInfo:
    """测试 TargetDeviceInfo 模型."""

    def test_create_target_info(self):
        """测试创建目标设备信息."""
        info = TargetDeviceInfo(
            device_name="FC7300F4MDSxXxxxT1C",
            core_type="Cortex-M7",
            core_id=0x6BC0C000,
            device_id=0x00000000,
            flash_size=4 * 1024 * 1024,  # 4MB
            ram_size=256 * 1024,  # 256KB
            ram_addresses=[(0x20000000, 0x20010000)]
        )
        assert info.device_name == "FC7300F4MDSxXxxxT1C"
        assert info.core_type == "Cortex-M7"
        assert info.flash_size == 4 * 1024 * 1024
        assert info.ram_size == 256 * 1024


# ==================== Operations Models ====================

class TestMemoryReadRequest:
    """测试 MemoryReadRequest 模型."""

    def test_valid_read_request(self):
        """测试有效的读取请求."""
        request = MemoryReadRequest(
            address=0x20000000,
            size=100,
            width=32
        )
        assert request.address == 0x20000000
        assert request.size == 100
        assert request.width == 32

    def test_invalid_size_negative(self):
        """测试无效大小（负数）."""
        with pytest.raises(ValidationError):
            MemoryReadRequest(address=0x20000000, size=-1, width=32)

    def test_invalid_size_too_large(self):
        """测试无效大小（过大）."""
        with pytest.raises(ValidationError):
            MemoryReadRequest(address=0x20000000, size=100000, width=32)

    def test_invalid_width(self):
        """测试无效宽度."""
        with pytest.raises(ValidationError):
            MemoryReadRequest(address=0x20000000, size=100, width=64)


class TestMemoryWriteRequest:
    """测试 MemoryWriteRequest 模型."""

    def test_valid_write_request(self):
        """测试有效的写入请求."""
        request = MemoryWriteRequest(
            address=0x20000000,
            data=bytes([0x01, 0x02, 0x03, 0x04]),
            width=32
        )
        assert request.address == 0x20000000
        assert request.data == bytes([0x01, 0x02, 0x03, 0x04])
        assert request.width == 32

    def test_empty_data(self):
        """测试空数据."""
        with pytest.raises(ValidationError):
            MemoryWriteRequest(address=0x20000000, data=b"", width=32)


class TestRegisterReadResult:
    """测试 RegisterReadResult 模型."""

    def test_create_register_result(self):
        """测试创建寄存器结果."""
        result = RegisterReadResult(
            register_name="R0",
            value=0x12345678,
            description="General Purpose Register 0"
        )
        assert result.register_name == "R0"
        assert result.value == 0x12345678
        assert result.description == "General Purpose Register 0"


# ==================== SVD Models ====================

class TestEnumeratedValue:
    """测试 EnumeratedValue 模型."""

    def test_create_enum_value(self):
        """测试创建枚举值."""
        enum = EnumeratedValue(
            name="Enabled",
            value=0,
            description="Enable the feature"
        )
        assert enum.name == "Enabled"
        assert enum.value == 0
        assert enum.description == "Enable the feature"


class TestFieldInfo:
    """测试 FieldInfo 模型."""

    def test_create_field(self):
        """测试创建字段."""
        field = FieldInfo(
            name="MDIS",
            description="Module Disable",
            bit_offset=31,
            bit_width=1,
            access="read-write",
            enumerated_values=[
                EnumeratedValue(name="Enabled", value=0, description="Enable")
            ]
        )
        assert field.name == "MDIS"
        assert field.bit_offset == 31
        assert field.bit_width == 1
        assert len(field.enumerated_values) == 1


class TestRegisterInfo:
    """测试 RegisterInfo 模型."""

    def test_create_register(self):
        """测试创建寄存器."""
        register = RegisterInfo(
            name="MCR",
            description="Module Configuration",
            address_offset=0x0,
            size=32,
            access="read-write",
            reset_value=0x0,
            fields=[]
        )
        assert register.name == "MCR"
        assert register.address_offset == 0x0
        assert register.size == 32


class TestPeripheralInfo:
    """测试 PeripheralInfo 模型."""

    def test_create_peripheral(self):
        """测试创建外设."""
        peripheral = PeripheralInfo(
            name="FLEXCAN0",
            description="FlexCAN Module 0",
            group_name="CAN",
            base_address=0x40080000,
            registers=[]
        )
        assert peripheral.name == "FLEXCAN0"
        assert peripheral.base_address == 0x40080000


class TestCPUInfo:
    """测试 CPUInfo 模型."""

    def test_create_cpu_info(self):
        """测试创建 CPU 信息."""
        cpu = CPUInfo(
            name="CM7",
            revision="r0p1",
            endian="little",
            mpu_present=True,
            fpu_present=True,
            nvic_prio_bits=4
        )
        assert cpu.name == "CM7"
        assert cpu.mpu_present is True
        assert cpu.fpu_present is True


class TestDeviceSVD:
    """测试 DeviceSVD 模型."""

    def test_create_device(self):
        """测试创建设备."""
        cpu = CPUInfo(
            name="CM7",
            revision="r0p1",
            endian="little",
            mpu_present=True,
            fpu_present=True,
            nvic_prio_bits=4
        )

        peripheral = PeripheralInfo(
            name="FLEXCAN0",
            description="FlexCAN Module 0",
            group_name="CAN",
            base_address=0x40080000,
            registers=[]
        )

        device = DeviceSVD(
            name="FC7300F4MDSxXxxxT1C",
            vendor="Flagchip",
            version="1.0",
            cpu=cpu,
            peripherals=[peripheral]
        )

        assert device.name == "FC7300F4MDSxXxxxT1C"
        assert device.vendor == "Flagchip"
        assert len(device.peripherals) == 1


class TestRegisterFieldResult:
    """测试 RegisterFieldResult 模型."""

    def test_create_field_result(self):
        """测试创建字段结果."""
        result = RegisterFieldResult(
            field_name="MDIS",
            field_value=0,
            field_value_hex="0x0",
            field_description="Module Disable",
            enum_name="Enabled",
            enum_description="Enable the module",
            bit_range="[31:31]",
            access="read-write"
        )
        assert result.field_name == "MDIS"
        assert result.field_value == 0
        assert result.enum_name == "Enabled"


class TestRegisterReadWithFieldsResult:
    """测试 RegisterReadWithFieldsResult 模型."""

    def test_create_register_with_fields(self):
        """测试创建带字段的寄存器结果."""
        field_result = RegisterFieldResult(
            field_name="MDIS",
            field_value=0,
            field_value_hex="0x0",
            field_description="Module Disable",
            enum_name="Enabled",
            enum_description="Enable the module",
            bit_range="[31:31]",
            access="read-write"
        )

        result = RegisterReadWithFieldsResult(
            device_name="FC7300F4MDSxXxxxT1C",
            peripheral_name="FLEXCAN0",
            register_name="MCR",
            register_description="Module Configuration",
            absolute_address=0x40080000,
            raw_value=0x0,
            hex_value="0x0",
            binary_value="00000000000000000000000000000000",
            access="read-write",
            reset_value="0x0",
            fields=[field_result],
            field_count=1
        )

        assert result.device_name == "FC7300F4MDSxXxxxT1C"
        assert result.peripheral_name == "FLEXCAN0"
        assert result.field_count == 1
        assert len(result.fields) == 1


# ==================== 边界测试 ====================

class TestBoundaryConditions:
    """测试边界条件."""

    def test_memory_size_max(self):
        """测试最大内存大小."""
        request = MemoryReadRequest(
            address=0x20000000,
            size=65536,  # 64KB
            width=32
        )
        assert request.size == 65536

    def test_memory_size_max_plus_one(self):
        """测试超过最大内存大小."""
        with pytest.raises(ValidationError):
            MemoryReadRequest(
                address=0x20000000,
                size=65537,  # 64KB + 1
                width=32
            )

    def test_field_bit_width_32(self):
        """测试 32 位字段."""
        field = FieldInfo(
            name="FULL32",
            description="32-bit field",
            bit_offset=0,
            bit_width=32,
            access="read-write"
        )
        assert field.bit_width == 32

    def test_field_bit_width_invalid(self):
        """测试无效位宽."""
        with pytest.raises(ValidationError):
            FieldInfo(
                name="INVALID",
                description="Invalid field",
                bit_offset=0,
                bit_width=33,  # 超过 32 位
                access="read-write"
            )
