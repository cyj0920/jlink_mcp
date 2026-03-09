"""工具函数 Mock 测试.

使用 Mock 对象测试工具函数，不依赖实际硬件。
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call

from jlink_mcp.tools.connection import (
    list_jlink_devices,
    connect_device,
    disconnect_device,
    get_connection_status
)

from jlink_mcp.tools.memory import (
    read_memory,
    write_memory,
    read_registers,
    write_register
)

from jlink_mcp.tools.svd import (
    list_svd_devices,
    get_svd_peripherals,
    get_svd_registers,
    parse_register_value
)

from jlink_mcp.exceptions import JLinkMCPError, JLinkErrorCode
from jlink_mcp.models.device import TargetInterface


# ==================== 连接管理测试 ====================

class TestListJLinkDevices:
    """测试列出 JLink 设备."""

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_list_devices_success(self, mock_manager):
        """测试成功列出设备."""
        # 设置 mock 返回值
        mock_manager.enumerate_devices.return_value = [
            Mock(serial_number="941000024", product_name="J-Link", firmware_version="V11.0.0")
        ]

        result = list_jlink_devices()

        assert result["success"] is True
        assert len(result) == 1
        assert result[0]["serial_number"] == "941000024"

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_list_devices_no_devices(self, mock_manager):
        """测试无设备."""
        mock_manager.enumerate_devices.return_value = []

        result = list_jlink_devices()

        assert result["success"] is True
        assert len(result) == 0

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_list_devices_error(self, mock_manager):
        """测试列出设备失败."""
        mock_manager.enumerate_devices.side_effect = Exception("Test error")

        result = list_jlink_devices()

        assert result["success"] is False
        assert "error" in result


class TestConnectDevice:
    """测试连接设备."""

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_connect_success(self, mock_manager):
        """测试成功连接."""
        mock_manager.connect.return_value = None
        mock_manager.get_connection_status.return_value = Mock(
            device_serial="941000024",
            target_interface=TargetInterface.SWD
        )

        result = connect_device(
            serial_number="941000024",
            interface="SWD",
            chip_name=None
        )

        assert result["success"] is True
        assert result["serial_number"] == "941000024"

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_connect_already_connected(self, mock_manager):
        """测试已连接."""
        mock_manager.connect.side_effect = JLinkMCPError(
            JLinkErrorCode.ALREADY_CONNECTED,
            "Already connected"
        )

        result = connect_device(
            serial_number="941000024",
            interface="SWD",
            chip_name=None
        )

        assert result["success"] is False
        assert "error" in result

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_connect_device_not_found(self, mock_manager):
        """测试设备未找到."""
        mock_manager.connect.side_effect = JLinkMCPError(
            JLinkErrorCode.DEVICE_NOT_FOUND,
            "Device not found"
        )

        result = connect_device(
            serial_number="999999999",
            interface="SWD",
            chip_name=None
        )

        assert result["success"] is False


class TestDisconnectDevice:
    """测试断开设备."""

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_disconnect_success(self, mock_manager):
        """测试成功断开."""
        mock_manager.disconnect.return_value = None

        result = disconnect_device()

        assert result["success"] is True

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_disconnect_not_connected(self, mock_manager):
        """测试未连接时断开."""
        mock_manager.disconnect.return_value = None

        result = disconnect_device()

        assert result["success"] is True


class TestGetConnectionStatus:
    """测试获取连接状态."""

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_get_status_connected(self, mock_manager):
        """测试获取已连接状态."""
        mock_status = Mock(
            connected=True,
            device_serial="941000024",
            target_interface=TargetInterface.SWD,
            target_voltage=3.3,
            target_connected=True,
            firmware_version="V11.0.0"
        )
        mock_manager.get_connection_status.return_value = mock_status

        result = get_connection_status()

        assert result["success"] is True
        assert result["data"]["connected"] is True
        assert result["data"]["device_serial"] == "941000024"

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_get_status_not_connected(self, mock_manager):
        """测试获取未连接状态."""
        mock_status = Mock(
            connected=False,
            device_serial=None,
            target_interface=None,
            target_voltage=None,
            target_connected=False,
            firmware_version=None
        )
        mock_manager.get_connection_status.return_value = mock_status

        result = get_connection_status()

        assert result["success"] is True
        assert result["data"]["connected"] is False


# ==================== 内存操作测试 ====================

class TestReadMemory:
    """测试读取内存."""

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_read_memory_success(self, mock_manager):
        """测试成功读取内存."""
        mock_jlink = Mock()
        mock_jlink.memory_read.return_value = bytes([0x01, 0x02, 0x03, 0x04])
        mock_manager.get_jlink.return_value = mock_jlink

        result = read_memory(address=0x20000000, size=4, width=32)

        assert result["success"] is True
        assert len(result["data"]) == 4
        assert result["data"][0] == 0x01

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_read_memory_invalid_size(self, mock_manager):
        """测试无效大小."""
        result = read_memory(address=0x20000000, size=-1, width=32)

        assert result["success"] is False
        assert "error" in result

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_read_memory_invalid_width(self, mock_manager):
        """测试无效宽度."""
        result = read_memory(address=0x20000000, size=4, width=64)

        assert result["success"] is False


class TestWriteMemory:
    """测试写入内存."""

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_write_memory_success(self, mock_manager):
        """测试成功写入内存."""
        mock_jlink = Mock()
        mock_jlink.memory_write.return_value = None
        mock_manager.get_jlink.return_value = mock_jlink

        result = write_memory(
            address=0x20000000,
            data=bytes([0x01, 0x02, 0x03, 0x04]),
            width=32
        )

        assert result["success"] is True
        assert result["bytes_written"] == 4

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_write_memory_empty_data(self, mock_manager):
        """测试空数据."""
        result = write_memory(
            address=0x20000000,
            data=b"",
            width=32
        )

        assert result["success"] is False


class TestReadRegisters:
    """测试读取寄存器."""

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_read_registers_success(self, mock_manager):
        """测试成功读取寄存器."""
        mock_jlink = Mock()
        mock_jlink.register_read.return_value = 0x12345678
        mock_manager.get_jlink.return_value = mock_jlink

        result = read_registers(register_names=["R0", "R1"])

        assert result["success"] is True
        assert len(result["registers"]) == 2

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_read_registers_all(self, mock_manager):
        """测试读取所有寄存器."""
        mock_jlink = Mock()
        mock_jlink.register_read.return_value = 0x0
        mock_manager.get_jlink.return_value = mock_jlink

        result = read_registers()

        assert result["success"] is True
        assert len(result["registers"]) > 0


class TestWriteRegister:
    """测试写入寄存器."""

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_write_register_success(self, mock_manager):
        """测试成功写入寄存器."""
        mock_jlink = Mock()
        mock_jlink.register_write.return_value = None
        mock_manager.get_jlink.return_value = mock_jlink

        result = write_register(register_name="R0", value=0x12345678)

        assert result["success"] is True
        assert result["value"] == 0x12345678

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_write_register_empty_name(self, mock_manager):
        """测试空寄存器名."""
        result = write_register(register_name="", value=0x12345678)

        assert result["success"] is False


# ==================== SVD 工具测试 ====================

class TestListSVDDevices:
    """测试列出 SVD 设备."""

    @patch('jlink_mcp.tools.svd.svd_manager')
    def test_list_svd_devices_success(self, mock_manager):
        """测试成功列出 SVD 设备."""
        mock_manager.is_available.return_value = True
        mock_manager.device_names = ["FC7300F4MDSxXxxxT1C", "FC7240F2MDSxXxxxT1A"]

        result = list_svd_devices()

        assert result["success"] is True
        assert result["count"] == 2
        assert "FC7300F4MDSxXxxxT1C" in result["devices"]

    @patch('jlink_mcp.tools.svd.svd_manager')
    def test_list_svd_devices_not_available(self, mock_manager):
        """测试 SVD 不可用."""
        mock_manager.is_available.return_value = False

        result = list_svd_devices()

        assert result["success"] is False
        assert "error" in result


class TestGetSVDPeripherals:
    """测试获取 SVD 外设."""

    @patch('jlink_mcp.tools.svd.svd_manager')
    def test_get_peripherals_success(self, mock_manager):
        """测试成功获取外设."""
        mock_manager.is_available.return_value = True

        mock_peripheral = Mock(
            name="FLEXCAN0",
            description="FlexCAN Module 0",
            group_name="CAN",
            base_address=0x40080000,
            registers=[]
        )
        mock_manager.get_peripherals.return_value = [mock_peripheral]

        result = get_svd_peripherals("FC7300F4MDSxXxxxT1C")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["peripherals"][0]["name"] == "FLEXCAN0"

    @patch('jlink_mcp.tools.svd.svd_manager')
    def test_get_peripherals_device_not_found(self, mock_manager):
        """测试设备未找到."""
        mock_manager.is_available.return_value = True
        mock_manager.get_peripherals.return_value = []

        result = get_svd_peripherals("InvalidDevice")

        assert result["success"] is True
        assert result["count"] == 0


class TestGetSVDRegisters:
    """测试获取 SVD 寄存器."""

    @patch('jlink_mcp.tools.svd.svd_manager')
    def test_get_registers_success(self, mock_manager):
        """测试成功获取寄存器."""
        mock_manager.is_available.return_value = True

        mock_peripheral = Mock(
            name="FLEXCAN0",
            description="FlexCAN Module 0",
            base_address=0x40080000
        )

        mock_register = Mock(
            name="MCR",
            description="Module Configuration",
            address_offset=0x0,
            size=32,
            access="read-write",
            reset_value=0,
            fields=[]
        )
        mock_peripheral.registers = [mock_register]

        mock_manager.get_peripheral.return_value = mock_peripheral

        result = get_svd_registers("FC7300F4MDSxXxxxT1C", "FLEXCAN0")

        assert result["success"] is True
        assert result["count"] == 1
        assert result["registers"][0]["name"] == "MCR"


class TestParseRegisterValue:
    """测试解析寄存器值."""

    @patch('jlink_mcp.tools.svd.svd_manager')
    def test_parse_value_success(self, mock_manager):
        """测试成功解析值."""
        mock_manager.is_available.return_value = True

        mock_field = Mock(
            name="ENABLE",
            description="Enable",
            bit_offset=0,
            bit_width=1,
            access="read-write"
        )
        mock_field.field_value = 1
        mock_field.field_value_hex = "0x1"
        mock_field.enum_name = "Enabled"
        mock_field.enum_description = "Feature enabled"
        mock_field.bit_range = "[0:0]"

        mock_register = Mock(
            name="CTRL",
            description="Control",
            fields=[mock_field]
        )

        mock_manager.parse_register_value.return_value = {
            "raw_value": 0x1,
            "hex_value": "0x1",
            "fields": [mock_field]
        }

        result = parse_register_value("FC7300F4MDSxXxxxT1C", "FLEXCAN0", "CTRL", 0x1)

        assert result["success"] is True
        assert result["raw_value"] == 0x1

    @patch('jlink_mcp.tools.svd.svd_manager')
    def test_parse_value_not_found(self, mock_manager):
        """测试寄存器未找到."""
        mock_manager.is_available.return_value = True
        mock_manager.parse_register_value.return_value = None

        result = parse_register_value("FC7300F4MDSxXxxxT1C", "FLEXCAN0", "Invalid", 0x1)

        assert result["success"] is False


# ==================== 边界测试 ====================

class TestBoundaryConditions:
    """测试边界条件."""

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_read_memory_max_size(self, mock_manager):
        """测试最大读取大小."""
        mock_jlink = Mock()
        mock_jlink.memory_read.return_value = bytes(65536)
        mock_manager.get_jlink.return_value = mock_jlink

        result = read_memory(address=0x20000000, size=65536, width=32)

        assert result["success"] is True

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_read_memory_exceeds_max_size(self, mock_manager):
        """测试超过最大读取大小."""
        result = read_memory(address=0x20000000, size=65537, width=32)

        assert result["success"] is False

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_write_memory_large_data(self, mock_manager):
        """测试写入大数据."""
        mock_jlink = Mock()
        mock_jlink.memory_write.return_value = None
        mock_manager.get_jlink.return_value = mock_jlink

        large_data = bytes(10000)
        result = write_memory(address=0x20000000, data=large_data, width=32)

        assert result["success"] is True
        assert result["bytes_written"] == 10000


# ==================== 错误处理测试 ====================

class TestErrorHandling:
    """测试错误处理."""

    @patch('jlink_mcp.tools.connection.jlink_manager')
    def test_connection_exception(self, mock_manager):
        """测试连接异常."""
        mock_manager.connect.side_effect = Exception("Connection failed")

        result = connect_device(serial_number="941000024", interface="SWD")

        assert result["success"] is False

    @patch('jlink_mcp.tools.memory.jlink_manager')
    def test_memory_read_exception(self, mock_manager):
        """测试内存读取异常."""
        mock_jlink = Mock()
        mock_jlink.memory_read.side_effect = Exception("Read failed")
        mock_manager.get_jlink.return_value = mock_jlink

        result = read_memory(address=0x20000000, size=4, width=32)

        assert result["success"] is False