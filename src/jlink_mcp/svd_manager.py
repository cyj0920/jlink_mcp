"""SVD File Manager - Singleton Pattern / SVD 文件管理器 - 单例模式管理 SVD 解析和查询.

Responsible for loading and parsing all SVD files, providing query interfaces
for chips, peripherals, registers, and fields.
负责加载和解析所有 SVD 文件，提供芯片、外设、寄存器、字段的查询接口。

Optimization Features / 优化特性:
- Lazy Loading / 延迟加载: Only load corresponding SVD file on first device access / 只在首次访问设备时加载对应的 SVD 文件
- Pickle Cache / Pickle 缓存: Parsed data cached to disk for fast hot start / 解析后的数据缓存到磁盘，热启动极速加载
- Index Lookup / 索引查找: Peripherals and registers use dict index, O(1) complexity / 外设和寄存器使用字典索引，O(1) 复杂度
- Pre-computation / 预计算: Field mask values and enum dict pre-computed during parsing / 字段 mask 值和枚举字典在解析时预计算
- Cache / 缓存: Use LRU cache for frequently queried results / 使用 LRU 缓存频繁查询的结果
"""

from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from functools import lru_cache
import xml.etree.ElementTree as ET
import pickle
import hashlib
import os

from .models.svd import (
    DeviceSVD, PeripheralInfo, RegisterInfo, FieldInfo,
    CPUInfo, EnumeratedValue
)
from .utils import logger


class SVDManager:
    """SVD 文件管理器（单例模式）.

    负责加载和解析所有 SVD 文件，提供芯片、外设、寄存器、字段的查询接口。
    使用延迟加载、Pickle 缓存和索引优化查询性能。
    """

    _instance: Optional["SVDManager"] = None
    _initialized: bool = False

    # 缓存版本号，当模型结构变化时需要更新
    CACHE_VERSION = 2

    def __new__(cls) -> "SVDManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if SVDManager._initialized:
            return

        # 优先使用外部SVD目录（通过环境变量）
        external_svd_dir = os.environ.get("JLINK_SVD_DIR")
        if external_svd_dir:
            self._svd_path = Path(external_svd_dir)
            logger.info(f"使用外部SVD目录: {external_svd_dir}")
        else:
            # 获取包目录（src/jlink_mcp）
            current_dir = Path(__file__).resolve().parent
            self._svd_path = current_dir / "tool" / "SVD_V1.5.6"
            logger.info(f"使用包内SVD目录: {self._svd_path}")

        # Pickle 缓存目录
        current_dir = Path(__file__).resolve().parent
        self._cache_dir = current_dir / ".svd_cache"
        self._cache_dir.mkdir(exist_ok=True)

        # 存储已加载的设备 SVD 数据
        self._devices: Dict[str, DeviceSVD] = {}

        # 设备名称到 SVD 文件路径的映射（延迟加载用）
        self._svd_file_map: Dict[str, Path] = {}

        # 外设索引: {device_name: {peripheral_name: PeripheralInfo}}
        self._peripheral_index: Dict[str, Dict[str, PeripheralInfo]] = {}

        # 寄存器索引: {device_name: {peripheral_name: {register_name: RegisterInfo}}}
        self._register_index: Dict[str, Dict[str, Dict[str, RegisterInfo]]] = {}

        # 仅扫描 SVD 文件，不加载内容
        self._scan_svd_files()

        SVDManager._initialized = True
        logger.debug(f"SVDManager 初始化完成，发现 {len(self._svd_file_map)} 个 SVD 文件")

    def _scan_svd_files(self) -> None:
        """扫描 SVD 目录，建立设备名到文件的映射（不解析内容）."""
        if not self._svd_path.exists():
            logger.warning(f"SVD 目录不存在: {self._svd_path}")
            return

        svd_files = list(self._svd_path.glob("*.svd"))
        for svd_file in svd_files:
            # 从文件名提取设备名（去掉 .svd 后缀）
            device_name = svd_file.stem
            self._svd_file_map[device_name] = svd_file

        logger.info(f"扫描发现 {len(self._svd_file_map)} 个 SVD 文件")

    def _get_cache_path(self, device_name: str) -> Path:
        """获取设备的缓存文件路径."""
        return self._cache_dir / f"{device_name}.v{self.CACHE_VERSION}.pkl"

    def _is_cache_valid(self, svd_path: Path, cache_path: Path) -> bool:
        """检查缓存是否有效.

        缓存有效的条件：
        1. 缓存文件存在
        2. 缓存文件的修改时间晚于 SVD 文件
        3. 缓存版本匹配
        """
        if not cache_path.exists():
            return False
        # 检查修改时间
        return cache_path.stat().st_mtime > svd_path.stat().st_mtime

    def _load_from_cache(self, device_name: str) -> Optional[DeviceSVD]:
        """从 Pickle 缓存加载设备数据."""
        cache_path = self._get_cache_path(device_name)
        svd_path = self._svd_file_map.get(device_name)
        
        if svd_path and not self._is_cache_valid(svd_path, cache_path):
            logger.debug(f"缓存已过期或不存在: {device_name}")
            return None

        try:
            with open(cache_path, 'rb') as f:
                device = pickle.load(f)
                logger.info(f"从缓存加载 SVD: {device_name}")
                return device
        except Exception as e:
            logger.warning(f"加载缓存失败 {device_name}: {e}")
            return None

    def _save_to_cache(self, device_name: str, device: DeviceSVD) -> None:
        """保存设备数据到 Pickle 缓存."""
        cache_path = self._get_cache_path(device_name)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(device, f)
                logger.debug(f"保存缓存: {device_name}")
        except Exception as e:
            logger.warning(f"保存缓存失败 {device_name}: {e}")

    def clear_cache_dir(self) -> None:
        """清除所有 Pickle 缓存文件."""
        import shutil
        if self._cache_dir.exists():
            shutil.rmtree(self._cache_dir)
            self._cache_dir.mkdir(exist_ok=True)
            logger.info("已清除所有 SVD 缓存")

    def _ensure_device_loaded(self, device_name: str) -> bool:
        """确保指定设备的 SVD 已加载.

        Args:
            device_name: 设备名称

        Returns:
            是否成功加载或已存在
        """
        # 如果设备已加载，直接返回成功
        if device_name in self._devices:
            return True

        # 尝试从 SVD 文件映射中加载
        svd_file = self._svd_file_map.get(device_name)
        if svd_file is None:
            # 尝试模糊匹配设备名
            matched_name = self._find_matching_device(device_name)
            if matched_name:
                device_name = matched_name
                svd_file = self._svd_file_map.get(device_name)
            else:
                # 设备不在文件映射中，但可能已通过其他方式添加（如测试）
                # 检查是否有类似的设备名已加载
                for loaded_name in self._devices:
                    if loaded_name.lower() == device_name.lower():
                        return True
                logger.warning(f"未找到设备 {device_name} 的 SVD 文件")
                return False

        try:
            # 1. 尝试从缓存加载
            device = self._load_from_cache(device_name)
            
            if device is None:
                # 2. 解析 SVD 文件
                logger.info(f"延迟加载 SVD 文件: {device_name}")
                device = self._parse_svd_file(svd_file)
                
                if device:
                    # 3. 保存到缓存
                    self._save_to_cache(device_name, device)
            
            if device:
                self._devices[device_name] = device
                self._build_index(device_name, device)
                return True
        except Exception as e:
            logger.error(f"加载 SVD 文件失败 {svd_file.name}: {e}")

        return False

    def _find_matching_device(self, partial_name: str) -> Optional[str]:
        """模糊匹配设备名称.

        Args:
            partial_name: 部分设备名称

        Returns:
            匹配到的完整设备名称，或 None
        """
        partial_lower = partial_name.lower()

        # 1. 精确匹配（忽略大小写）
        for name in self._svd_file_map:
            if name.lower() == partial_lower:
                return name

        # 2. 前缀匹配
        matches = [name for name in self._svd_file_map if name.lower().startswith(partial_lower)]
        if len(matches) == 1:
            return matches[0]
        elif matches:
            # 优先选择非解锁版本
            normal = [n for n in matches if "Unlock" not in n and "Factory" not in n]
            if normal:
                return normal[0]
            return matches[0]

        return None

    def _build_index(self, device_name: str, device: DeviceSVD) -> None:
        """为设备的所有外设和寄存器建立索引.

        Args:
            device_name: 设备名称
            device: 设备 SVD 数据
        """
        # 建立外设索引
        peripheral_idx: Dict[str, PeripheralInfo] = {}
        register_idx: Dict[str, Dict[str, RegisterInfo]] = {}

        for peripheral in device.peripherals:
            peripheral_idx[peripheral.name] = peripheral

            # 建立寄存器索引
            reg_idx: Dict[str, RegisterInfo] = {}
            for register in peripheral.registers:
                reg_idx[register.name] = register
            register_idx[peripheral.name] = reg_idx

        self._peripheral_index[device_name] = peripheral_idx
        self._register_index[device_name] = register_idx

        logger.debug(f"为 {device_name} 建立索引: {len(peripheral_idx)} 外设")

    def _parse_svd_file(self, svd_path: Path) -> Optional[DeviceSVD]:
        """解析单个 SVD 文件."""
        tree = ET.parse(svd_path)
        root = tree.getroot()

        # 解析设备基本信息
        device = DeviceSVD(
            name=root.findtext("name", ""),
            vendor=root.findtext("vendor", ""),
            version=root.findtext("version", ""),
            description=root.findtext("description", ""),
            cpu=self._parse_cpu(root.find("cpu")),
            peripherals=[]
        )

        # 解析外设
        peripherals = root.find("peripherals")
        if peripherals is not None:
            for peripheral in peripherals.findall("peripheral"):
                device.peripherals.append(self._parse_peripheral(peripheral))

        return device

    def _parse_cpu(self, cpu_element) -> CPUInfo:
        """解析 CPU 信息."""
        if cpu_element is None:
            return CPUInfo(name="Unknown")

        return CPUInfo(
            name=cpu_element.findtext("name", ""),
            revision=cpu_element.findtext("revision"),
            endian=cpu_element.findtext("endian"),
            mpu_present=cpu_element.findtext("mpuPresent", "false") == "true",
            fpu_present=cpu_element.findtext("fpuPresent", "false") == "true",
            nvic_prio_bits=self._parse_int(cpu_element.findtext("nvicPrioBits", "0"))
        )

    def _parse_peripheral(self, peripheral) -> PeripheralInfo:
        """解析外设信息."""
        registers_element = peripheral.find("registers")
        registers = []
        if registers_element is not None:
            for register in registers_element.findall("register"):
                registers.append(self._parse_register(register))

        return PeripheralInfo(
            name=peripheral.findtext("name", ""),
            description=peripheral.findtext("description"),
            group_name=peripheral.findtext("groupName"),
            base_address=self._parse_int(peripheral.findtext("baseAddress", "0")),
            registers=registers
        )

    def _parse_register(self, register) -> RegisterInfo:
        """解析寄存器信息."""
        fields_element = register.find("fields")
        fields = []
        if fields_element is not None:
            for field in fields_element.findall("field"):
                fields.append(self._parse_field(field))

        return RegisterInfo(
            name=register.findtext("name", ""),
            description=register.findtext("description"),
            address_offset=self._parse_int(register.findtext("addressOffset", "0")),
            size=self._parse_int(register.findtext("size", "32")),
            access=register.findtext("access"),
            reset_value=self._parse_int(register.findtext("resetValue")),
            fields=fields
        )

    def _parse_field(self, field) -> FieldInfo:
        """解析字段信息（包含预计算的 bit_mask 和 enum_map）."""
        bit_width = self._parse_int(field.findtext("bitWidth", "1")) or 1
        bit_mask = (1 << bit_width) - 1  # 预计算 mask

        # 解析枚举值并预计算 enum_map
        enum_element = field.find("enumeratedValues")
        enumerated_values = []
        enum_map: Dict[int, Tuple[str, Optional[str]]] = {}
        
        if enum_element is not None:
            for enum_value in enum_element.findall("enumeratedValue"):
                val = self._parse_int(enum_value.findtext("value", "0"))
                if val is not None:
                    name = enum_value.findtext("name", "")
                    desc = enum_value.findtext("description")
                    enumerated_values.append(EnumeratedValue(
                        name=name,
                        value=val,
                        description=desc
                    ))
                    # 预计算 enum_map 用于 O(1) 查找
                    enum_map[val] = (name, desc)

        return FieldInfo(
            name=field.findtext("name", ""),
            description=field.findtext("description"),
            bit_offset=self._parse_int(field.findtext("bitOffset", "0")) or 0,
            bit_width=bit_width,
            bit_mask=bit_mask,  # 预计算的 mask
            access=field.findtext("access"),
            reset_value=self._parse_int(field.findtext("resetValue")),
            enumerated_values=enumerated_values,
            enum_map=enum_map  # 预计算的枚举字典
        )

    @staticmethod
    def _parse_int(value: Optional[str]) -> Optional[int]:
        """解析整数值（支持十进制和十六进制）."""
        if value is None:
            return None
        value = value.strip()
        if value.startswith("0x") or value.startswith("0X"):
            return int(value, 16)
        return int(value)

    # ==================== 查询接口 ====================

    def is_available(self) -> bool:
        """检查 SVD 是否可用."""
        return len(self._svd_file_map) > 0

    @property
    def device_names(self) -> List[str]:
        """获取所有设备名称."""
        return list(self._svd_file_map.keys())

    def get_device(self, device_name: str) -> Optional[DeviceSVD]:
        """获取指定设备的 SVD 信息."""
        if self._ensure_device_loaded(device_name):
            # 返回实际加载的设备名
            actual_name = self._find_matching_device(device_name) or device_name
            return self._devices.get(actual_name)
        return None

    @lru_cache(maxsize=32)
    def _get_peripherals_cached(self, device_name: str) -> Tuple[PeripheralInfo, ...]:
        """获取指定设备的所有外设（内部缓存方法）.

        Returns:
            外设元组（不可变，支持缓存）
        """
        if self._ensure_device_loaded(device_name):
            actual_name = self._find_matching_device(device_name) or device_name
            device = self._devices.get(actual_name)
            if device:
                return tuple(device.peripherals)
        return ()

    def get_peripherals(self, device_name: str) -> List[PeripheralInfo]:
        """获取指定设备的所有外设.

        Returns:
            外设列表
        """
        return list(self._get_peripherals_cached(device_name))

    def get_peripheral(self, device_name: str, peripheral_name: str) -> Optional[PeripheralInfo]:
        """获取指定外设（O(1) 索引查找，索引不存在时回退到线性查找）."""
        if self._ensure_device_loaded(device_name):
            actual_name = self._find_matching_device(device_name) or device_name
            
            # 优先使用索引
            peripheral_idx = self._peripheral_index.get(actual_name, {})
            if peripheral_idx:
                return peripheral_idx.get(peripheral_name)
            
            # 索引不存在时回退到线性查找（兼容直接设置 _devices 的情况）
            device = self._devices.get(actual_name)
            if device:
                for peripheral in device.peripherals:
                    if peripheral.name == peripheral_name:
                        return peripheral
        return None

    def get_register(self, device_name: str, peripheral_name: str, register_name: str) -> Optional[RegisterInfo]:
        """获取指定寄存器（O(1) 索引查找，索引不存在时回退到线性查找）."""
        if self._ensure_device_loaded(device_name):
            actual_name = self._find_matching_device(device_name) or device_name
            
            # 优先使用索引
            register_idx = self._register_index.get(actual_name, {})
            peripheral_regs = register_idx.get(peripheral_name, {})
            if peripheral_regs:
                return peripheral_regs.get(register_name)
            
            # 索引不存在时回退到线性查找（兼容直接设置 _devices 的情况）
            peripheral = self.get_peripheral(device_name, peripheral_name)
            if peripheral:
                for register in peripheral.registers:
                    if register.name == register_name:
                        return register
        return None

    def parse_register_value(
        self,
        device_name: str,
        peripheral_name: str,
        register_name: str,
        value: int
    ) -> Optional[Dict[str, Any]]:
        """解析寄存器值，返回各字段的解释（使用预计算的 mask 和 enum_map，O(1) 枚举查找）."""
        register = self.get_register(device_name, peripheral_name, register_name)
        if not register:
            return None

        field_results = []
        for field in register.fields:
            # 使用预计算的 mask，如果为 0 则动态计算（向后兼容）
            bit_mask = field.bit_mask if field.bit_mask > 0 else ((1 << field.bit_width) - 1)
            field_value = (value >> field.bit_offset) & bit_mask

            # 使用预计算的 enum_map 进行 O(1) 查找
            enum_name = None
            enum_description = None
            
            if field.enum_map:
                # O(1) 字典查找
                enum_name, enum_description = field.enum_map.get(field_value, (None, None))
            else:
                # 回退到线性查找（向后兼容）
                for enum in field.enumerated_values:
                    if enum.value == field_value:
                        enum_name = enum.name
                        enum_description = enum.description
                        break

            field_results.append({
                "field_name": field.name,
                "field_value": field_value,
                "field_value_hex": f"0x{field_value:X}",
                "field_description": field.description,
                "enum_name": enum_name,
                "enum_description": enum_description,
                "bit_range": f"[{field.bit_offset}:{field.bit_offset + field.bit_width - 1}]",
                "access": field.access
            })

        return {
            "device_name": device_name,
            "peripheral_name": peripheral_name,
            "register_name": register_name,
            "register_description": register.description,
            "raw_value": value,
            "hex_value": f"0x{value:X}",
            "binary_value": format(value, f'0{register.size}b'),
            "fields": field_results
        }

    def clear_cache(self) -> None:
        """清除查询缓存."""
        self._get_peripherals_cached.cache_clear()
        logger.debug("SVD 查询缓存已清除")


# 全局单例
svd_manager = SVDManager()