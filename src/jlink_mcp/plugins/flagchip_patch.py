"""Flagchip JLink Patch Plugin / Flagchip JLink 补丁插件.

Implements DevicePatchInterface, providing device patch support for Flagchip vendor.
实现 DevicePatchInterface，提供 Flagchip 厂商的设备补丁支持。

Optimization Features / 优化特性:
- Pre-computed lowercase name dict, O(1) exact match / 预计算小写名称字典，O(1) 精确匹配
- Single traversal for prefix matching / 单次遍历完成前缀匹配
- Cached match results / 缓存匹配结果
"""

from pathlib import Path
from typing import List, Dict, Any, Optional
from functools import lru_cache
import os

from ..device_patch_interface import DevicePatchInterface
from ..utils import logger


class FlagchipPatch(DevicePatchInterface):
    """Flagchip JLink 补丁插件.

    实现 DevicePatchInterface 接口，提供 Flagchip 设备的名称匹配和查询功能。
    """

    def __init__(self):
        """初始化补丁插件."""
        # 优先使用外部JLink补丁目录（通过环境变量）
        external_patch_dir = os.environ.get("JLINK_PATCH_DIR")
        if external_patch_dir:
            self._patch_path = Path(external_patch_dir) / "JLink_Patch_v2.45" / "JLinkDevices.xml"
            logger.info(f"使用外部JLink补丁目录: {external_patch_dir}")
        else:
            # 获取包目录（src/jlink_mcp）
            current_dir = Path(__file__).resolve().parent.parent
            self._patch_path = current_dir / "tool" / "JLink_Patch_v2.45" / "JLinkDevices.xml"
            logger.info(f"使用包内JLink补丁目录: {self._patch_path}")

        self._devices: List[Dict[str, Any]] = []

        # 优化: 预计算的数据结构
        self._device_names: List[str] = []
        self._device_names_lower: Dict[str, str] = {}  # {lower_name: original_name}
        self._device_names_lower_list: List[str] = []  # 小写名称列表（用于前缀匹配）

        self._load_devices()

    @property
    def vendor_name(self) -> str:
        """获取补丁厂商名称."""
        return "Flagchip"

    @property
    def patch_version(self) -> str:
        """获取补丁版本号."""
        return "v2.45"

    def _load_devices(self) -> None:
        """从 XML 文件加载设备信息."""
        if not self._patch_path.exists():
            logger.warning(f"Flagchip 补丁文件不存在: {self._patch_path}")
            return

        try:
            import xml.etree.ElementTree as ET
            tree = ET.parse(self._patch_path)
            root = tree.getroot()

            for device in root.findall("Device"):
                chip_info = device.find("ChipInfo")
                if chip_info is not None:
                    name = chip_info.get("Name", "")
                    self._devices.append({
                        "name": name,
                        "vendor": chip_info.get("Vendor", ""),
                        "core": chip_info.get("Core", ""),
                        "work_ram_addr": chip_info.get("WorkRAMAddr", ""),
                        "work_ram_size": chip_info.get("WorkRAMSize", ""),
                    })
                    # 预计算小写名称
                    self._device_names.append(name)
                    self._device_names_lower[name.lower()] = name
                    self._device_names_lower_list.append(name.lower())

            logger.info(f"从补丁文件加载了 {len(self._devices)} 个 {self.vendor_name} 设备")

        except Exception as e:
            logger.error(f"加载 {self.vendor_name} 补丁失败: {e}")

    def is_available(self) -> bool:
        """检查补丁是否可用."""
        return len(self._devices) > 0

    @property
    def devices(self) -> List[Dict[str, Any]]:
        """获取所有设备."""
        return self._devices

    @property
    def device_names(self) -> List[str]:
        """获取所有设备名称."""
        return self._device_names

    @lru_cache(maxsize=128)
    def match_device_name(self, partial_name: str) -> Optional[str]:
        """智能匹配设备名称（增强版）.

        支持多种匹配模式：
        1. 精确匹配（忽略大小写）
        2. 前缀匹配：FC7300F4MDD -> FC7300F4MDDxXxxxT1C
        3. 包含匹配：FC7300F4MDDS -> FC7300F4MDSxXxxxT1C
        4. 占位符模糊匹配：FC7300F4MDDxT1C -> FC7300F4MDDxXxxxT1C

        Args:
            partial_name: 部分或简化的设备名称

        Returns:
            匹配到的完整设备名称，如果无法匹配则返回 None
        """
        if not partial_name:
            return None

        partial_name = partial_name.strip()
        partial_lower = partial_name.lower()

        # 1. O(1) 精确匹配（忽略大小写）
        if partial_lower in self._device_names_lower:
            return self._device_names_lower[partial_lower]

        # 2. 前缀匹配（单次遍历）
        prefix_matches: List[str] = []
        contains_matches: List[str] = []
        fuzzy_matches: List[str] = []

        # 预处理输入：移除常见的占位符模式
        # 如 FC7300F4MDDxT1C -> FC7300F4MDD (用于模糊匹配)
        fuzzy_pattern = self._create_fuzzy_pattern(partial_lower)

        for i, name_lower in enumerate(self._device_names_lower_list):
            original_name = self._device_names[i]

            # 前缀匹配
            if name_lower.startswith(partial_lower):
                prefix_matches.append(original_name)
            # 包含匹配
            elif partial_lower in name_lower:
                contains_matches.append(original_name)
            # 占位符模糊匹配
            elif fuzzy_pattern and fuzzy_pattern in name_lower:
                fuzzy_matches.append(original_name)

        # 合并匹配结果，优先级：前缀 > 包含 > 模糊
        all_matches = prefix_matches + contains_matches + fuzzy_matches

        if not all_matches:
            return None

        # 去重（保持顺序）
        seen = set()
        matches = []
        for m in all_matches:
            if m not in seen:
                seen.add(m)
                matches.append(m)

        # 如果只有一个匹配，直接返回
        if len(matches) == 1:
            return matches[0]

        # 多个匹配时，优先选择非解锁/非工厂模式的设备
        normal_devices = [
            name for name in matches
            if not any(keyword in name for keyword in ["Unlock", "Factory", "FromRom", "Core", "_64", "ETM"])
        ]

        if not normal_devices:
            normal_devices = matches

        # 按照批次版本优先级排序: T1C > T1B > T1A
        def get_revision_priority(name: str) -> int:
            if "T1C" in name:
                return 3
            elif "T1B" in name:
                return 2
            elif "T1A" in name:
                return 1
            return 0

        normal_devices.sort(key=lambda name: (-get_revision_priority(name), len(name)))
        return normal_devices[0]

    def _create_fuzzy_pattern(self, partial_lower: str) -> Optional[str]:
        """创建模糊匹配模式.

        处理用户输入中的占位符模式，如：
        - FC7300F4MDDxT1C -> fc7300f4mdd (移除 xT1C 后缀)
        - FC7300F4MDDXT1C -> fc7300f4mdd (大写 X 也处理)
        """
        import re
        # 移除末尾的版本后缀模式 (x/xx/xxx/X/Xx/Xxxx + T1A/T1B/T1C 等)
        pattern = re.sub(r'x*x*x*t\d+[a-z]$', '', partial_lower)
        if pattern != partial_lower and len(pattern) >= 6:
            return pattern
        return None

    def find_similar_devices(self, partial_name: str, limit: int = 5) -> List[str]:
        """查找相似的设备名称（优化版：单次遍历）.

        Args:
            partial_name: 部分设备名称
            limit: 返回结果的最大数量

        Returns:
            相似的设备名称列表
        """
        if not partial_name:
            return self._device_names[:limit]

        partial_lower = partial_name.strip().lower()

        # 单次遍历，同时收集前缀匹配和包含匹配
        starts_with: List[str] = []
        contains: List[str] = []

        for i, name_lower in enumerate(self._device_names_lower_list):
            original_name = self._device_names[i]
            if name_lower.startswith(partial_lower):
                starts_with.append(original_name)
            elif partial_lower in name_lower:
                contains.append(original_name)

        # 合并结果，优先显示前缀匹配的
        results = starts_with + contains

        return results[:limit]

    def get_device_name_suggestions(self, partial_name: str) -> str:
        """获取设备名称建议的格式化字符串.

        Args:
            partial_name: 部分设备名称

        Returns:
            格式化的建议字符串
        """
        similar = self.find_similar_devices(partial_name, limit=5)

        if not similar:
            return f"未找到与 '{partial_name}' 相似的设备。\n支持的设备: {', '.join(self._device_names[:10])}..."

        suggestions = "\n".join(f"  - {name}" for name in similar)
        return f"您是否想找以下设备之一:\n{suggestions}"

    def clear_cache(self) -> None:
        """清除匹配缓存."""
        self.match_device_name.cache_clear()
        logger.debug(f"{self.vendor_name} 设备匹配缓存已清除")


# 创建单例实例（可选加载）
def create_flagchip_patch() -> Optional[FlagchipPatch]:
    """创建 Flagchip 补丁实例.

    Returns:
        如果补丁可用，返回 FlagchipPatch 实例；否则返回 None
    """
    patch = FlagchipPatch()
    if patch.is_available():
        return patch
    return None


# 全局单例（向后兼容）
flagchip_patch = FlagchipPatch()