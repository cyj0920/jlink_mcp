"""Device Patch Plugins Module / 设备补丁插件模块.

Provides plugin-based device patch support, supporting dynamic loading of
device patches from multiple vendors.
提供插件化设备补丁支持，支持多种厂商的设备补丁动态加载。
"""

from .flagchip_patch import FlagchipPatch

__all__ = ["FlagchipPatch"]