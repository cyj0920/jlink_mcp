"""测试辅助模块 - Fixtures 和 Mock 工具.

提供测试所需的共享 fixtures、mock 对象和辅助函数。
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, MagicMock, patch
import pytest

# 添加项目路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))


# ==================== Mock 对象 ====================

class MockJLink:
    """模拟 JLink 对象."""

    def __init__(self):
        self.serial_number = "941000024"
        self.firmware_version = "V11.0.0"
        self._connected = False
        self._target_connected = False
        self._memory = {}
        self._registers = {}

    def open(self, serial_no: Optional[str] = None):
        """打开连接."""
        self._connected = True
        return True

    def close(self):
        """关闭连接."""
        self._connected = False
        self._target_connected = False

    def set_tif(self, interface):
        """设置接口类型."""
        pass

    def connect(self, chip_name: str = ""):
        """连接目标."""
        self._target_connected = True
        return True

    def target_connected(self) -> bool:
        """检查目标是否连接."""
        return self._target_connected

    def target_voltage(self) -> float:
        """获取目标电压."""
        return 3.3

    def core_name(self) -> str:
        """获取内核名称."""
        return "Cortex-M7"

    def core_id(self) -> int:
        """获取内核 ID."""
        return 0x6BC0C000

    def device_name(self) -> Optional[str]:
        """获取设备名称."""
        return "FC7300F4MDSxXxxxT1C"

    def device_id(self) -> Optional[int]:
        """获取设备 ID."""
        return 0x00000000

    def memory_read(self, address: int, size: int) -> bytes:
        """读取内存."""
        # 返回模拟数据
        return bytes([i % 256 for i in range(size)])

    def memory_write(self, address: int, data: bytes):
        """写入内存."""
        self._memory[address] = data

    def register_read(self, name: str) -> int:
        """读取寄存器."""
        # 返回模拟值
        reg_map = {
            "R0": 0xDEADBEEF,
            "R1": 0x12345678,
            "R2": 0x87654321,
            "R3": 0x11111111,
            "R4": 0x22222222,
            "R5": 0x33333333,
            "R6": 0x44444444,
            "R7": 0x55555555,
            "R8": 0x66666666,
            "R9": 0x77777777,
            "R10": 0x88888888,
            "R11": 0x99999999,
            "R12": 0xAAAAAAAA,
            "SP": 0x21000000,
            "LR": 0x08000000,
            "PC": 0x08000100,
            "XPSR": 0x01000000,
            "MSP": 0x21000000,
            "PSP": 0x00000000,
        }
        return reg_map.get(name, 0)

    def register_write(self, name: str, value: int):
        """写入寄存器."""
        self._registers[name] = value

    def halt(self) -> bool:
        """暂停 CPU."""
        return True

    def go(self) -> bool:
        """运行 CPU."""
        return True

    def step(self) -> bool:
        """单步执行."""
        return True

    def reset(self) -> bool:
        """复位目标."""
        return True

    def set_breakpoint(self, address: int) -> bool:
        """设置断点."""
        return True

    def clear_breakpoint(self, address: int) -> bool:
        """清除断点."""
        return True

    def version(self) -> str:
        """获取固件版本."""
        return self.firmware_version


class MockEmulator:
    """模拟 JLink 设备."""

    def __init__(self, serial_number: str = "941000024"):
        self.SerialNumber = serial_number
        self.ProductName = "J-Link"


# ==================== Fixtures ====================

@pytest.fixture
def mock_jlink():
    """Mock JLink 对象."""
    return MockJLink()


@pytest.fixture
def mock_emulator():
    """Mock JLink 设备."""
    return MockEmulator()


@pytest.fixture
def mock_pylink():
    """Mock pylink 库."""
    with patch('pylink.JLink') as mock:
        mock.return_value = MockJLink()
        yield mock


@pytest.fixture
def sample_svd_content():
    """示例 SVD 内容."""
    return """<?xml version='1.0' encoding='utf-8'?>
<device schemaVersion="1.1">
  <vendor>Flagchip</vendor>
  <name>FC7300F4MDSxXxxxT1C</name>
  <version>1.0</version>
  <cpu>
    <name>CM7</name>
    <revision>r0p1</revision>
    <endian>little</endian>
    <mpuPresent>true</mpuPresent>
    <fpuPresent>true</fpuPresent>
    <nvicPrioBits>4</nvicPrioBits>
  </cpu>
  <peripherals>
    <peripheral>
      <name>FLEXCAN0</name>
      <description>FlexCAN Module 0</description>
      <groupName>CAN</groupName>
      <baseAddress>0x40080000</baseAddress>
      <registers>
        <register>
          <name>MCR</name>
          <description>Module Configuration Register</description>
          <addressOffset>0x0</addressOffset>
          <size>32</size>
          <access>read-write</access>
          <resetValue>0x00000000</resetValue>
          <fields>
            <field>
              <name>MDIS</name>
              <description>Module Disable</description>
              <bitOffset>31</bitOffset>
              <bitWidth>1</bitWidth>
              <access>read-write</access>
              <enumeratedValues>
                <enumeratedValue>
                  <name>Enabled</name>
                  <value>0</value>
                  <description>Enable the module</description>
                </enumeratedValue>
                <enumeratedValue>
                  <name>Disabled</name>
                  <value>1</value>
                  <description>Disable the module</description>
                </enumeratedValue>
              </enumeratedValues>
            </field>
            <field>
              <name>HALT</name>
              <description>Halt FlexCAN</description>
              <bitOffset>16</bitOffset>
              <bitWidth>1</bitWidth>
              <access>read-write</access>
            </field>
          </fields>
        </register>
      </registers>
    </peripheral>
  </peripherals>
</device>"""


@pytest.fixture
def sample_svd_file(tmp_path, sample_svd_content):
    """创建临时 SVD 文件."""
    svd_file = tmp_path / "test_device.svd"
    svd_file.write_text(sample_svd_content)
    return svd_file


@pytest.fixture
def mock_svd_manager():
    """Mock SVD 管理器."""
    from jlink_mcp.models.svd import (
        DeviceSVD, PeripheralInfo, RegisterInfo, FieldInfo,
        EnumeratedValue, CPUInfo
    )

    # 创建模拟设备
    cpu = CPUInfo(
        name="CM7",
        revision="r0p1",
        endian="little",
        mpu_present=True,
        fpu_present=True,
        nvic_prio_bits=4
    )

    field1 = FieldInfo(
        name="MDIS",
        description="Module Disable",
        bit_offset=31,
        bit_width=1,
        access="read-write",
        enumerated_values=[
            EnumeratedValue(name="Enabled", value=0, description="Enable the module"),
            EnumeratedValue(name="Disabled", value=1, description="Disable the module")
        ]
    )

    field2 = FieldInfo(
        name="HALT",
        description="Halt FlexCAN",
        bit_offset=16,
        bit_width=1,
        access="read-write"
    )

    register = RegisterInfo(
        name="MCR",
        description="Module Configuration Register",
        address_offset=0x0,
        size=32,
        access="read-write",
        reset_value=0,
        fields=[field1, field2]
    )

    peripheral = PeripheralInfo(
        name="FLEXCAN0",
        description="FlexCAN Module 0",
        group_name="CAN",
        base_address=0x40080000,
        registers=[register]
    )

    device = DeviceSVD(
        name="FC7300F4MDSxXxxxT1C",
        vendor="Flagchip",
        version="1.0",
        cpu=cpu,
        peripherals=[peripheral]
    )

    # 创建 Mock 管理器
    manager = MagicMock()
    manager.is_available.return_value = True
    manager.device_names = ["FC7300F4MDSxXxxxT1C"]
    manager.get_device.return_value = device
    manager.get_peripherals.return_value = device.peripherals
    manager.get_peripheral.return_value = peripheral
    manager.get_register.return_value = register

    return manager


# ==================== 辅助函数 ====================

def create_mock_response(success: bool, data: Any = None, error: Optional[Dict[str, Any]] = None):
    """创建模拟响应."""
    response = {"success": success}
    if success:
        response["data"] = data
    else:
        response["error"] = error or {
            "code": 1,
            "description": "Test error",
            "suggestion": "Test suggestion"
        }
    return response


def create_mock_error(code: int = 1, description: str = "Test error", suggestion: str = "Test suggestion"):
    """创建模拟错误."""
    return {
        "code": code,
        "description": description,
        "suggestion": suggestion
    }