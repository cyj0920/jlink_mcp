"""JLink Device Manager - Singleton Pattern / JLink 设备管理器 - 单例模式管理 JLink 连接."""

import pylink
from typing import Optional, List
from contextlib import contextmanager

from .config_manager import config_manager
from .device_patch_manager import device_patch_manager
from .exceptions import (
    JLinkMCPError,
    JLinkErrorCode,
    DeviceNotFoundError,
    ConnectionError,
    OperationError,
)
from .models.device import (
    ConnectionMode,
    ConnectionStatus,
    DeviceInfo,
    TargetDeviceInfo,
    TargetInterface,
)
from .utils import logger


AUTO_CHIP_NAME_MARKERS = {"", "auto", "autodetect", "auto-detect"}
COMMON_AUTO_DETECT_CHIPS = [
    "STM32F407VG", "STM32F103C8", "STM32L431RC",
    "nRF52832_xxAA", "ESP32", "MK64FN1M0xxx12"
]


class JLinkManager:
    """JLink 设备管理器（单例模式）.

    管理单个 JLink 设备的连接、断开和状态查询。
    确保同一时间只有一个连接存在。
    """

    _instance: Optional["JLinkManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "JLinkManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if JLinkManager._initialized:
            return

        self._jlink: Optional[pylink.JLink] = None
        self._connected: bool = False
        self._device_serial: Optional[str] = None
        self._target_interface: TargetInterface = TargetInterface.JTAG
        self._target_connected: bool = False
        self._connection_mode: Optional[ConnectionMode] = None
        self._connection_strategy: Optional[str] = None
        self._requested_chip_name: Optional[str] = None
        self._connected_chip_name: Optional[str] = None

        JLinkManager._initialized = True
        logger.debug("JLinkManager 初始化完成")

    @property
    def is_connected(self) -> bool:
        """检查是否已连接到 JLink 设备."""
        if self._jlink is None:
            return False
        try:
            _ = self._jlink.serial_number
            return True
        except Exception:
            return False

    @property
    def is_target_connected(self) -> bool:
        """检查目标芯片是否已连接."""
        if not self.is_connected or self._jlink is None:
            return False
        try:
            return self._jlink.target_connected()
        except Exception:
            return False

    @property
    def connection_mode(self) -> Optional[str]:
        """返回当前连接模式字符串."""
        return self._connection_mode.value if self._connection_mode else None

    @property
    def connection_strategy(self) -> Optional[str]:
        """返回当前连接策略."""
        return self._connection_strategy

    @property
    def requested_chip_name(self) -> Optional[str]:
        """返回用户请求的芯片名称."""
        return self._requested_chip_name

    @property
    def connected_chip_name(self) -> Optional[str]:
        """返回最终连接到的芯片或核心名称."""
        return self._connected_chip_name

    def enumerate_devices(self) -> List[DeviceInfo]:
        """枚举所有连接的 JLink 设备.

        Returns:
            设备信息列表
        """
        devices = []
        try:
            usb_devices = pylink.JLink().connected_emulators()
            for dev in usb_devices:
                serial_number = getattr(dev, 'SerialNumber', 'Unknown')
                product_name = getattr(dev, 'ProductName', None) or getattr(dev, 'ProductName', 'J-Link')
                if product_name is None:
                    product_name = "J-Link"

                device_info = DeviceInfo(
                    serial_number=str(serial_number),
                    product_name=product_name,
                    firmware_version="Unknown",
                    connection_type="USB",
                    hardware_version=None,
                )
                devices.append(device_info)

            logger.info(f"发现 {len(devices)} 个 JLink 设备")
            return devices

        except Exception as e:
            logger.error(f"枚举设备失败: {e}")
            return []

    def connect(
        self,
        serial_number: Optional[str] = None,
        interface: TargetInterface = TargetInterface.JTAG,
        chip_name: Optional[str] = None,
    ) -> None:
        """连接到 JLink 设备.

        Args:
            serial_number: 设备序列号，None 则连接第一个可用设备
            interface: 目标接口类型（SWD/JTAG）
            chip_name: 目标芯片名称（如 STM32F407VG），None 则尝试自动检测

        Raises:
            AlreadyConnectedError: 如果已连接
            DeviceNotFoundError: 如果未找到设备
            ConnectionError: 如果连接失败
        """
        if self.is_connected:
            raise JLinkMCPError(
                JLinkErrorCode.ALREADY_CONNECTED,
                f"已连接到设备 {self._device_serial}",
            )

        try:
            self._jlink = pylink.JLink()
            normalized_chip_name = self._normalize_chip_name(chip_name)
            self._requested_chip_name = normalized_chip_name

            if serial_number:
                logger.info(f"正在连接设备: {serial_number}")
                self._jlink.open(serial_no=serial_number)
            else:
                logger.info("正在连接第一个可用设备")
                self._jlink.open()

            self._target_interface = interface
            if interface == TargetInterface.SWD:
                self._jlink.set_tif(pylink.JLinkInterfaces.SWD)
            elif interface == TargetInterface.JTAG:
                self._jlink.set_tif(pylink.JLinkInterfaces.JTAG)
            else:
                raise ConnectionError(f"不支持的接口类型: {interface}")

            if normalized_chip_name:
                self._connect_named_target(normalized_chip_name)
            else:
                self._auto_connect_target()

            self._target_connected = self._jlink.target_connected()
            self._connected = True
            self._device_serial = self._jlink.serial_number

            logger.info(
                "成功连接到设备: %s, mode=%s, strategy=%s, target=%s",
                self._device_serial,
                self.connection_mode,
                self.connection_strategy,
                self._connected_chip_name,
            )

        except JLinkMCPError:
            self._cleanup()
            raise
        except Exception as e:
            self._cleanup()
            if "not found" in str(e).lower():
                raise DeviceNotFoundError(f"设备 {serial_number} 未找到", e)
            raise ConnectionError(str(e), e)

    def _normalize_chip_name(self, chip_name: Optional[str]) -> Optional[str]:
        """Normalize chip name input / 规范化芯片名输入."""
        if chip_name is None:
            return None

        normalized = chip_name.strip()
        if normalized.lower() in AUTO_CHIP_NAME_MARKERS:
            return None

        return normalized

    def _is_generic_core_name(self, chip_name: Optional[str]) -> bool:
        """Check whether chip name is a generic core / 判断是否为通用核心名."""
        if not chip_name:
            return False
        return chip_name.strip().lower().startswith("cortex-")

    def _get_generic_core_name(self, preferred: Optional[str] = None) -> str:
        """Return generic core fallback target / 获取通用核心回退名称."""
        if self._is_generic_core_name(preferred):
            return preferred.strip()

        default_core = config_manager.get_config().default_core.strip()
        return default_core or "Cortex-M4"

    def _resolve_connected_chip_name(self, fallback: Optional[str] = None) -> Optional[str]:
        """Resolve connected chip name from J-Link / 从 J-Link 获取实际连接名称."""
        if self._jlink is None:
            return fallback

        try:
            device_name = self._jlink.device_name()
            if device_name:
                return str(device_name)
        except Exception:
            pass

        return fallback

    def _set_connection_context(
        self,
        mode: ConnectionMode,
        strategy: str,
        connected_chip_name: Optional[str],
    ) -> None:
        """Store current connection context / 记录当前连接上下文."""
        self._connection_mode = mode
        self._connection_strategy = strategy
        self._connected_chip_name = connected_chip_name

    def _try_connect_target(
        self,
        target_name: str,
        mode: ConnectionMode,
        strategy: str,
    ) -> Optional[str]:
        """Try connecting target and update mode metadata / 尝试连接目标并更新模式信息."""
        self._jlink.connect(target_name)
        connected_chip_name = self._resolve_connected_chip_name(target_name or None)
        self._set_connection_context(mode, strategy, connected_chip_name)
        return connected_chip_name

    def _connect_named_target(self, chip_name: str) -> None:
        """Connect using explicit chip name with layered strategy / 按显式芯片名进行分层连接."""
        errors: List[str] = []
        config = config_manager.get_config()

        explicit_mode = ConnectionMode.GENERIC if self._is_generic_core_name(chip_name) else ConnectionMode.NATIVE
        explicit_strategy = "explicit_generic_core" if explicit_mode == ConnectionMode.GENERIC else "explicit_native"

        try:
            logger.info("连接策略 1/3: 直接使用 J-Link 原生设备名 %s", chip_name)
            self._try_connect_target(chip_name, explicit_mode, explicit_strategy)
            return
        except Exception as native_error:
            logger.warning("J-Link 原生设备连接失败: %s", native_error)
            errors.append(f"native({chip_name}): {native_error}")

        match_result = device_patch_manager.match_device_name(chip_name)
        if match_result:
            matched_name, patch = match_result
            try:
                logger.info(
                    "连接策略 2/3: 使用私有补丁匹配 %s -> %s (%s)",
                    chip_name,
                    matched_name,
                    patch.vendor_name,
                )
                self._try_connect_target(
                    matched_name,
                    ConnectionMode.PRIVATE,
                    f"patch_match:{patch.vendor_name}",
                )
                return
            except Exception as patch_error:
                logger.warning("私有补丁设备连接失败: %s", patch_error)
                errors.append(f"private({matched_name}): {patch_error}")
        else:
            errors.append(f"private({chip_name}): no patch match")

        if config.generic_core_fallback:
            generic_core = self._get_generic_core_name(chip_name)
            if generic_core and generic_core != chip_name:
                try:
                    logger.info("连接策略 3/3: 使用通用核心回退 %s", generic_core)
                    self._try_connect_target(
                        generic_core,
                        ConnectionMode.GENERIC,
                        "generic_fallback",
                    )
                    return
                except Exception as generic_error:
                    logger.warning("通用核心回退连接失败: %s", generic_error)
                    errors.append(f"generic({generic_core}): {generic_error}")
        else:
            errors.append("generic fallback disabled")

        similar = device_patch_manager.find_similar_devices(chip_name, limit=5)
        suggestion = (
            f"\n您是否想找: {', '.join(similar)}"
            if similar
            else "\n如需通用核心调试，可启用 JLINK_GENERIC_CORE_FALLBACK 或显式传入 Cortex-M 系列核心名称"
        )
        raise ConnectionError(
            "无法连接到芯片 "
            f"'{chip_name}'。已尝试 native -> private patch -> generic fallback。"
            f"\n详细信息: {'; '.join(errors)}"
            f"{suggestion}",
            None,
        )

    def _auto_connect_target(self) -> None:
        """Auto-detect and connect target / 自动检测并连接目标芯片."""
        logger.info("尝试自动检测芯片...")
        config = config_manager.get_config()

        try:
            logger.info("自动检测策略 1/4: 让 J-Link 自动识别目标芯片")
            self._try_connect_target("", ConnectionMode.NATIVE, "auto_detect")
            logger.info("J-Link 自动识别芯片成功")
            return
        except Exception as autodetect_error:
            logger.warning(f"自动检测失败: {autodetect_error}")

        patch_devices = device_patch_manager.get_all_device_names()
        if patch_devices:
            logger.info(f"自动检测策略 2/4: 尝试设备补丁中的 {len(patch_devices)} 个设备")
            for chip in patch_devices:
                try:
                    logger.info(f"尝试补丁设备: {chip}")
                    self._try_connect_target(
                        chip,
                        ConnectionMode.PRIVATE,
                        "patch_scan",
                    )
                    logger.info(f"通过设备补丁成功连接到芯片: {chip}")
                    return
                except Exception:
                    continue

        if config.generic_core_fallback:
            generic_core = self._get_generic_core_name()
            try:
                logger.info(f"自动检测策略 3/4: 尝试通用核心回退 {generic_core}")
                self._try_connect_target(
                    generic_core,
                    ConnectionMode.GENERIC,
                    "generic_fallback",
                )
                logger.info(f"通过通用核心回退成功连接到目标: {generic_core}")
                return
            except Exception as generic_error:
                logger.warning(f"通用核心回退失败: {generic_error}")

        logger.info(f"自动检测策略 4/4: 尝试常见芯片列表 {COMMON_AUTO_DETECT_CHIPS}")
        for chip in COMMON_AUTO_DETECT_CHIPS:
            try:
                logger.info(f"尝试常见芯片: {chip}")
                self._try_connect_target(
                    chip,
                    ConnectionMode.NATIVE,
                    "common_chip_fallback",
                )
                logger.info(f"通过常见芯片回退成功连接到芯片: {chip}")
                return
            except Exception:
                continue

        patch_hint = f"设备补丁支持的设备: {patch_devices[:5]}...\n" if patch_devices else ""
        generic_hint = (
            f"默认通用核心: {self._get_generic_core_name()}\n"
            if config.generic_core_fallback
            else "通用核心回退已禁用，可通过 JLINK_GENERIC_CORE_FALLBACK 启用\n"
        )
        raise ConnectionError(
            "无法自动检测芯片，请手动指定芯片名称。\n"
            f"{patch_hint}"
            f"{generic_hint}"
            f"常见设备: {COMMON_AUTO_DETECT_CHIPS}",
            None,
        )

    def disconnect(self) -> None:
        """断开 JLink 连接."""
        if not self.is_connected:
            logger.debug("没有活动的连接")
            return

        logger.info("正在断开连接")
        self._cleanup()
        logger.info("连接已断开")

    def _cleanup(self) -> None:
        """清理资源."""
        if self._jlink:
            try:
                self._jlink.close()
            except Exception as e:
                logger.warning(f"关闭连接时出错: {e}")
            finally:
                self._jlink = None

        self._connected = False
        self._device_serial = None
        self._target_connected = False
        self._connection_mode = None
        self._connection_strategy = None
        self._requested_chip_name = None
        self._connected_chip_name = None

    def get_connection_status(self) -> ConnectionStatus:
        """获取连接状态.

        Returns:
            连接状态信息
        """
        if not self.is_connected or self._jlink is None:
            return ConnectionStatus(
                connected=False,
                device_serial=None,
                target_interface=None,
                target_voltage=None,
                target_connected=False,
                firmware_version=None,
                connection_mode=None,
                connection_strategy=None,
                requested_chip_name=None,
                connected_chip_name=None,
            )

        try:
            status = self._jlink.hardware_status
            voltage = status.VTarget / 1000.0
            fw_version = self._jlink.version
        except Exception as e:
            logger.warning(f"获取硬件状态失败: {e}")
            voltage = None
            fw_version = None

        device_serial = self._device_serial
        if device_serial is None:
            try:
                device_serial = self._jlink.serial_number
            except Exception as e:
                logger.warning(f"获取设备序列号失败: {e}")
                device_serial = "Unknown"

        return ConnectionStatus(
            connected=True,
            device_serial=device_serial,
            target_interface=self._target_interface,
            target_voltage=voltage,
            target_connected=self.is_target_connected,
            firmware_version=fw_version,
            connection_mode=self._connection_mode,
            connection_strategy=self._connection_strategy,
            requested_chip_name=self._requested_chip_name,
            connected_chip_name=self._connected_chip_name,
        )

    def get_target_info(self) -> TargetDeviceInfo:
        """获取目标设备信息.

        Returns:
            目标设备信息

        Raises:
            JLinkMCPError: 如果未连接或获取失败
        """
        self._ensure_connected()
        self._ensure_target_connected()

        try:
            jlink = self._jlink

            device_name = None
            try:
                device_name = jlink.device_name()
            except Exception:
                pass

            core_type = None
            core_id = None
            try:
                core_type = jlink.core_name()
                core_id = jlink.core_id()
            except Exception:
                pass

            device_id = None
            try:
                device_id = jlink.device_id()
            except Exception:
                pass

            flash_size = None
            ram_size = None
            ram_addresses = []

            try:
                if hasattr(jlink, 'device'):
                    device = jlink.device
                    if device:
                        flash_size = device.FlashSize
                        ram_size = device.RAMSize
            except Exception:
                pass

            return TargetDeviceInfo(
                device_name=device_name,
                core_type=core_type,
                core_id=core_id,
                device_id=device_id,
                flash_size=flash_size,
                ram_size=ram_size,
                ram_addresses=ram_addresses,
            )

        except JLinkMCPError:
            raise
        except Exception as e:
            raise OperationError(
                JLinkErrorCode.READ_FAILED,
                f"获取目标信息失败: {e}",
                e,
            )

    def get_jlink(self) -> pylink.JLink:
        """获取 JLink 实例.

        Returns:
            JLink 实例

        Raises:
            JLinkMCPError: 如果未连接
        """
        self._ensure_connected()
        return self._jlink

    def _ensure_connected(self) -> None:
        """确保已连接到 JLink 设备.

        Raises:
            JLinkMCPError: 如果未连接
        """
        if not self.is_connected:
            raise JLinkMCPError(
                JLinkErrorCode.NOT_INITIALIZED,
                "JLink 未连接",
            )

    def _ensure_target_connected(self) -> None:
        """确保目标芯片已连接.

        Raises:
            JLinkMCPError: 如果目标未连接
        """
        if not self.is_target_connected:
            raise JLinkMCPError(
                JLinkErrorCode.TARGET_NOT_CONNECTED,
                "目标芯片未连接",
            )

    @contextmanager
    def session(self):
        """上下文管理器，用于自动管理连接.

        示例:
            with jlink_manager.session():
                # 执行操作
                pass
        """
        try:
            yield self
        finally:
            if self.is_connected:
                self.disconnect()


jlink_manager = JLinkManager()
