"""设备补丁管理器.

统一管理所有设备补丁插件，提供设备名称匹配和查询的统一接口。
"""

from typing import List, Dict, Any, Optional
from .device_patch_interface import DevicePatchInterface
from .plugins import FlagchipPatch
from .utils import logger


class DevicePatchManager:
    """设备补丁管理器（单例模式）.

    管理所有已加载的设备补丁插件，提供统一的设备查询接口。
    """

    _instance: Optional["DevicePatchManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "DevicePatchManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if DevicePatchManager._initialized:
            return

        self._patches: List[DevicePatchInterface] = []
        self._patch_index: Dict[str, DevicePatchInterface] = {}  # {vendor: patch}

        # 自动加载可用的补丁
        self._load_available_patches()

        DevicePatchManager._initialized = True
        logger.debug(f"DevicePatchManager 初始化完成，加载了 {len(self._patches)} 个补丁")

    def _load_available_patches(self) -> None:
        """自动加载所有可用的设备补丁."""
        # 加载 Flagchip 补丁
        try:
            flagchip_patch = FlagchipPatch()
            if flagchip_patch.is_available():
                self._patches.append(flagchip_patch)
                self._patch_index[flagchip_patch.vendor_name.lower()] = flagchip_patch
                logger.info(f"加载设备补丁: {flagchip_patch.vendor_name} {flagchip_patch.patch_version}")
        except Exception as e:
            logger.warning(f"加载 Flagchip 补丁失败: {e}")

    def register_patch(self, patch: DevicePatchInterface) -> None:
        """注册新的设备补丁.

        Args:
            patch: 设备补丁实例
        """
        vendor_key = patch.vendor_name.lower()

        if vendor_key in self._patch_index:
            logger.warning(f"补丁 {patch.vendor_name} 已存在，将被替换")

        self._patch_index[vendor_key] = patch
        self._patches = list(self._patch_index.values())
        logger.info(f"注册设备补丁: {patch.vendor_name} {patch.patch_version}")

    def unregister_patch(self, vendor_name: str) -> bool:
        """注销设备补丁.

        Args:
            vendor_name: 厂商名称

        Returns:
            如果成功注销，返回 True
        """
        vendor_key = vendor_name.lower()
        if vendor_key in self._patch_index:
            patch = self._patch_index.pop(vendor_key)
            self._patches = list(self._patch_index.values())
            logger.info(f"注销设备补丁: {patch.vendor_name}")
            return True
        return False

    def get_patch_by_vendor(self, vendor_name: str) -> Optional[DevicePatchInterface]:
        """根据厂商名称获取补丁.

        Args:
            vendor_name: 厂商名称

        Returns:
            设备补丁实例，如果未找到则返回 None
        """
        return self._patch_index.get(vendor_name.lower())

    def match_device_name(self, chip_name: str) -> Optional[tuple[str, DevicePatchInterface]]:
        """在所有补丁中匹配设备名称.

        Args:
            chip_name: 设备名称（可以是简化名称）

        Returns:
            元组 (matched_name, patch)，如果未匹配则返回 None
        """
        for patch in self._patches:
            matched = patch.match_device_name(chip_name)
            if matched:
                return matched, patch
        return None

    def find_similar_devices(self, chip_name: str, limit: int = 10) -> List[str]:
        """在所有补丁中查找相似的设备名称.

        Args:
            chip_name: 设备名称
            limit: 返回结果数量限制

        Returns:
            相似设备名称列表
        """
        all_matches: List[str] = []
        for patch in self._patches:
            matches = patch.find_similar_devices(chip_name, limit)
            all_matches.extend(matches)

        # 去重并限制数量
        seen = set()
        unique_matches = []
        for name in all_matches:
            if name not in seen:
                seen.add(name)
                unique_matches.append(name)
                if len(unique_matches) >= limit:
                    break

        return unique_matches

    def get_device_name_suggestions(self, chip_name: str) -> str:
        """获取设备名称建议.

        Args:
            chip_name: 设备名称

        Returns:
            格式化的建议字符串
        """
        all_matches = self.find_similar_devices(chip_name, limit=10)

        if not all_matches:
            supported_devices = []
            for patch in self._patches:
                supported_devices.extend(patch.device_names[:5])
            return f"未找到与 '{chip_name}' 相似的设备。\n支持的设备: {', '.join(supported_devices)}..."

        suggestions = "\n".join(f"  - {name}" for name in all_matches)
        return f"您是否想找以下设备之一:\n{suggestions}"

    def get_all_device_names(self) -> List[str]:
        """获取所有补丁支持的设备名称.

        Returns:
            设备名称列表
        """
        all_devices = []
        for patch in self._patches:
            all_devices.extend(patch.device_names)
        return all_devices

    def is_device_supported(self, device_name: str) -> bool:
        """检查设备是否被支持.

        Args:
            device_name: 设备名称

        Returns:
            如果设备被支持，返回 True
        """
        for patch in self._patches:
            if patch.supports_device(device_name):
                return True
        return False

    @property
    def available_patches(self) -> List[DevicePatchInterface]:
        """获取所有可用的补丁."""
        return self._patches.copy()

    @property
    def patch_count(self) -> int:
        """获取补丁数量."""
        return len(self._patches)

    @property
    def supported_vendor_names(self) -> List[str]:
        """获取支持的厂商名称列表."""
        return [patch.vendor_name for patch in self._patches]

    def get_patch_info(self) -> List[Dict[str, Any]]:
        """获取所有补丁的信息.

        Returns:
            补丁信息列表
        """
        return [
            {
                "vendor": patch.vendor_name,
                "version": patch.patch_version,
                "device_count": len(patch.device_names),
                "available": patch.is_available()
            }
            for patch in self._patches
        ]


# 全局单例
device_patch_manager = DevicePatchManager()