"""J-Link GDB Server Management / J-Link GDB Server 管理."""

import threading
import time
from typing import Optional, Dict, Any

import pylink

from .jlink_manager import jlink_manager
from .exceptions import GDBServerError, JLinkErrorCode
from .models.device import TargetInterface, GDBServerStatus
from .utils import logger


class GDBServerManager:
    """GDB Server 管理器.

    管理 J-Link GDB Server 的启动、停止和状态查询。
    支持通过子进程启动 GDB Server，提供远程调试能力。
    """

    _instance: Optional["GDBServerManager"] = None
    _initialized: bool = False

    def __new__(cls) -> "GDBServerManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if GDBServerManager._initialized:
            return

        self._process: Optional[subprocess.Popen] = None
        self._running: bool = False
        self._host: str = "0.0.0.0"
        self._port: int = 2331
        self._device: Optional[str] = None
        self._interface: TargetInterface = TargetInterface.JTAG

        GDBServerManager._initialized = True
        logger.debug("GDBServerManager 初始化完成")

    @property
    def is_running(self) -> bool:
        """检查 GDB Server 是否正在运行."""
        if self._process is None:
            return False

        # 检查进程是否仍然存活
        if self._process.poll() is not None:
            logger.warning("GDB Server 进程已意外终止")
            self._cleanup()
            return False

        return self._running

    def start(
        self,
        host: str = "0.0.0.0",
        port: int = 2331,
        device: Optional[str] = None,
        interface: TargetInterface = TargetInterface.JTAG,
        speed: int = 4000
    ) -> None:
        """启动 GDB Server.

        Args:
            host: 监听地址（默认 0.0.0.0）
            port: 监听端口（默认 2331）
            device: 设备名称（None 则使用当前连接的设备）
            interface: 接口类型（默认 JTAG）
            speed: 接口速度（kHz，默认 4000）

        Raises:
            GDBServerError: 如果启动失败
        """
        if self.is_running:
            raise GDBServerError(
                JLinkErrorCode.GDB_SERVER_ALREADY_RUNNING,
                f"GDB Server 已在运行（端口 {self._port}）",
                "如需重启，请先调用 stop_gdb_server"
            )

        if not jlink_manager.is_connected:
            raise GDBServerError(
                JLinkErrorCode.NOT_INITIALIZED,
                "JLink 未连接",
                "请先调用 connect_device 建立连接"
            )

        try:
            import subprocess

            self._host = host
            self._port = port
            self._device = device
            self._interface = interface

            # 构建 GDB Server 命令
            jlink_exe = self._find_jlink_gdbserver_exe()
            if not jlink_exe:
                raise GDBServerError(
                    JLinkErrorCode.GDB_SERVER_START_FAILED,
                    "未找到 JLinkGDBServer.exe",
                    "请确保已安装 SEGGER JLink 软件并添加到系统 PATH"
                )

            cmd = [
                jlink_exe,
                "-device", device or "",
                "-if", interface.value.lower(),
                "-speed", str(speed),
                "-port", str(port)
            ]

            # 如果指定了序列号，添加序列号参数
            serial_number = jlink_manager._device_serial
            if serial_number:
                cmd.extend(["-select", "USB", "-usb", serial_number])

            logger.info(f"启动 GDB Server: {' '.join(cmd)}")

            # 启动进程
            self._process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW
            )

            # 等待进程启动
            time.sleep(0.5)

            if self._process.poll() is not None:
                stdout, stderr = self._process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') or stdout.decode('utf-8', errors='ignore')
                raise GDBServerError(
                    JLinkErrorCode.GDB_SERVER_START_FAILED,
                    f"GDB Server 启动失败: {error_msg}",
                    "请检查端口是否被占用，或查看 JLink 日志"
                )

            self._running = True
            logger.info(f"GDB Server 已启动，监听 {host}:{port}")

        except GDBServerError:
            self._cleanup()
            raise
        except Exception as e:
            self._cleanup()
            raise GDBServerError(
                JLinkErrorCode.GDB_SERVER_START_FAILED,
                f"启动 GDB Server 时发生异常: {e}",
                "请检查 JLink 软件是否正确安装"
            )

    def stop(self) -> None:
        """停止 GDB Server."""
        if not self.is_running:
            logger.debug("GDB Server 未运行")
            return

        logger.info("正在停止 GDB Server")
        self._cleanup()
        logger.info("GDB Server 已停止")

    def _cleanup(self) -> None:
        """清理资源."""
        if self._process:
            try:
                self._process.terminate()
                # 等待进程结束
                try:
                    self._process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._process.kill()
                    self._process.wait()
            except Exception as e:
                logger.warning(f"清理 GDB Server 进程时出错: {e}")
            finally:
                self._process = None

        self._running = False

    def get_status(self) -> GDBServerStatus:
        """获取 GDB Server 状态.

        Returns:
            GDB Server 状态信息
        """
        return GDBServerStatus(
            running=self.is_running,
            host=self._host if self._running else None,
            port=self._port if self._running else None,
            device_name=self._device,
            interface=self._interface if self._running else None
        )

    def _find_jlink_gdbserver_exe(self) -> Optional[str]:
        """查找 JLinkGDBServer.exe 可执行文件.

        Returns:
            可执行文件路径，如果未找到则返回 None
        """
        import subprocess
        import os

        # 尝试从 PATH 查找
        try:
            result = subprocess.run(
                ["where", "JLinkGDBServer.exe"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip().split('\n')[0]
        except Exception:
            pass

        # 尝试常见安装路径
        common_paths = [
            r"C:\Program Files\SEGGER\JLink",
            r"C:\Program Files (x86)\SEGGER\JLink",
        ]

        for base_path in common_paths:
            exe_path = os.path.join(base_path, "JLinkGDBServer.exe")
            if os.path.exists(exe_path):
                return exe_path

        return None


# 全局单例实例
gdb_server_manager = GDBServerManager()


def start_gdb_server(
    host: str = "0.0.0.0",
    port: int = 2331,
    device: Optional[str] = None,
    interface: str = "JTAG",
    speed: int = 4000
) -> Dict[str, Any]:
    """启动 GDB Server.

    Args:
        host: 监听地址（默认 0.0.0.0）
        port: 监听端口（默认 2331）
        device: 设备名称（None 则使用当前连接的设备）
        interface: 接口类型（SWD/JTAG，默认 SWD）
        speed: 接口速度（kHz，默认 4000）

    Returns:
        启动结果，包含:
        - success: 是否成功
        - host: 监听地址
        - port: 监听端口
        - message: 状态信息
    """
    try:
        interface_enum = TargetInterface(interface.upper())
        gdb_server_manager.start(host, port, device, interface_enum, speed)

        return {
            "success": True,
            "host": host,
            "port": port,
            "message": f"GDB Server 已启动，监听 {host}:{port}"
        }
    except GDBServerError as e:
        logger.error(f"启动 GDB Server 失败: {e}")
        return {
            "success": False,
            "host": host,
            "port": port,
            "error": e.to_dict()
        }
    except Exception as e:
        logger.error(f"启动 GDB Server 失败: {e}")
        return {
            "success": False,
            "host": host,
            "port": port,
            "error": {
                "code": JLinkErrorCode.GDB_SERVER_START_FAILED.value[0],
                "description": str(e),
                "suggestion": "请检查 JLink 软件是否正确安装并添加到 PATH"
            }
        }


def stop_gdb_server() -> Dict[str, Any]:
    """停止 GDB Server.

    Returns:
        停止结果，包含:
        - success: 是否成功
        - message: 状态信息
    """
    try:
        gdb_server_manager.stop()

        return {
            "success": True,
            "message": "GDB Server 已停止"
        }
    except Exception as e:
        logger.error(f"停止 GDB Server 失败: {e}")
        return {
            "success": False,
            "error": {
                "code": JLinkErrorCode.UNKNOWN_ERROR.value[0],
                "description": str(e),
                "suggestion": "请检查 GDB Server 状态"
            }
        }


def get_gdb_server_status() -> Dict[str, Any]:
    """获取 GDB Server 状态.

    Returns:
        GDB Server 状态，包含:
        - success: 是否成功
        - running: 是否正在运行
        - host: 监听地址
        - port: 监听端口
        - device_name: 设备名称
        - interface: 接口类型
    """
    try:
        status = gdb_server_manager.get_status()

        return {
            "success": True,
            "status": status.model_dump(),
            "message": "GDB Server 已启动" if status.running else "GDB Server 未运行"
        }
    except Exception as e:
        logger.error(f"获取 GDB Server 状态失败: {e}")
        return {
            "success": False,
            "error": {
                "code": JLinkErrorCode.UNKNOWN_ERROR.value[0],
                "description": str(e),
                "suggestion": "请检查 GDB Server 状态"
            }
        }