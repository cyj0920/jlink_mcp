"""Device Patch Abstract Interface / 设备补丁抽象层接口.

Defines the common interface for device patches, supporting plugin-based loading
for multiple vendors' device patches.
定义设备补丁的通用接口，支持多种厂商的设备补丁插件化加载。
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class DevicePatchInterface(ABC):
    """设备补丁抽象接口.

    所有设备补丁插件都必须实现此接口，以支持统一的设备名称匹配和查询。
    """

    @property
    @abstractmethod
    def vendor_name(self) -> str:
        """获取补丁厂商名称.

        Returns:
            厂商名称（如 "Flagchip", "STMicroelectronics"）
        """

    @property
    @abstractmethod
    def patch_version(self) -> str:
        """获取补丁版本号.

        Returns:
            版本号（如 "v2.45"）
        """

    @abstractmethod
    def is_available(self) -> bool:
        """检查补丁是否可用.

        Returns:
            如果补丁可用且已加载，返回 True
        """

    @property
    @abstractmethod
    def devices(self) -> List[Dict[str, Any]]:
        """获取所有支持的设备信息.

        Returns:
            设备信息列表，每个设备包含 name, vendor, core 等信息
        """

    @property
    @abstractmethod
    def device_names(self) -> List[str]:
        """获取所有支持的设备名称.

        Returns:
            设备名称列表
        """

    @abstractmethod
    def match_device_name(self, partial_name: str) -> Optional[str]:
        """智能匹配设备名称.

        支持多种匹配模式：
        - 精确匹配（忽略大小写）
        - 前缀匹配
        - 包含匹配
        - 模糊匹配

        Args:
            partial_name: 部分或简化的设备名称

        Returns:
            匹配到的完整设备名称，如果无法匹配则返回 None
        """

    @abstractmethod
    def find_similar_devices(self, partial_name: str, limit: int = 10) -> List[str]:
        """查找相似的设备名称.

        Args:
            partial_name: 部分设备名称
            limit: 返回结果数量限制

        Returns:
            相似设备名称列表
        """

    @abstractmethod
    def get_device_name_suggestions(self, partial_name: str) -> str:
        """获取设备名称建议字符串.

        Args:
            partial_name: 用户输入的部分设备名称

        Returns:
            格式化的建议字符串
        """

    def get_device_info(self, device_name: str) -> Optional[Dict[str, Any]]:
        """获取指定设备的详细信息.

        Args:
            device_name: 设备名称

        Returns:
            设备信息字典，如果未找到则返回 None
        """
        for device in self.devices:
            if device.get("name") == device_name:
                return device
        return None

    def supports_device(self, device_name: str) -> bool:
        """检查是否支持指定设备.

        Args:
            device_name: 设备名称

        Returns:
            如果支持该设备，返回 True
        """
        return device_name in self.device_names