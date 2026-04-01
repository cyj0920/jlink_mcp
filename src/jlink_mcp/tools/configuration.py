"""Configuration and capability tool functions / 配置与能力探测工具函数."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

from ..config_manager import config_manager
from ..device_patch_manager import device_patch_manager
from ..gdb_server import gdb_server_manager
from ..jlink_manager import jlink_manager
from ..svd_manager import svd_manager
from ..utils import logger


def _detect_resource_mode(private_patch_loaded: bool, svd_loaded: bool) -> str:
    """Infer resource mode / 推断资源模式."""
    if private_patch_loaded or svd_loaded:
        return "mixed"
    return "generic"


def get_server_config() -> Dict[str, Any]:
    """Get current server configuration / 获取当前服务器配置."""
    try:
        runtime = config_manager.get_runtime_config()
        return {
            "success": True,
            "data": runtime,
            "message": "Server configuration retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Failed to get server configuration: {e}")
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "message": "Failed to retrieve server configuration"
        }


def get_server_capabilities() -> Dict[str, Any]:
    """Get current server capabilities / 获取当前服务器能力状态."""
    try:
        config = config_manager.get_config()
        patch_info = device_patch_manager.get_patch_info()
        private_patch_loaded = device_patch_manager.patch_count > 0
        svd_loaded = svd_manager.is_available()
        gdb_server_path = gdb_server_manager._find_jlink_gdbserver_exe()

        capabilities = {
            "default_interface": config.default_interface,
            "generic_core_debug": True,
            "jlink_connected": jlink_manager.is_connected,
            "target_connected": jlink_manager.is_target_connected,
            "private_patch_loaded": private_patch_loaded,
            "patch_count": device_patch_manager.patch_count,
            "patch_device_count": len(device_patch_manager.get_all_device_names()),
            "patches": patch_info,
            "svd_loaded": svd_loaded,
            "svd_device_count": len(svd_manager.device_names),
            "gdb_server_binary_available": bool(gdb_server_path),
            "gdb_server_running": gdb_server_manager.is_running,
            "semantic_enabled": config.semantic_enabled,
            "resource_mode": _detect_resource_mode(private_patch_loaded, svd_loaded),
            "available_modes": [
                "native",
                "generic",
                *(
                    ["private"]
                    if private_patch_loaded or svd_loaded
                    else []
                )
            ]
        }

        return {
            "success": True,
            "data": capabilities,
            "message": "Server capabilities retrieved successfully"
        }
    except Exception as e:
        logger.error(f"Failed to get server capabilities: {e}")
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "message": "Failed to retrieve server capabilities"
        }


def diagnose_environment() -> Dict[str, Any]:
    """Diagnose environment and resource availability / 诊断环境与资源可用性."""
    try:
        config = config_manager.get_config()
        env_overrides = config_manager.get_env_config()

        svd_path = Path(config.svd_dir) if config.svd_dir else getattr(svd_manager, "_svd_path", None)
        patch_path = Path(config.patch_dir) if config.patch_dir else None
        if patch_path is not None:
            patch_manifest = patch_path / "JLink_Patch_v2.45" / "JLinkDevices.xml"
        else:
            first_patch = device_patch_manager.available_patches[0] if device_patch_manager.available_patches else None
            patch_manifest = Path(first_patch._patch_path) if first_patch is not None else None  # type: ignore[attr-defined]

        gdb_server_path = gdb_server_manager._find_jlink_gdbserver_exe()

        checks = {
            "default_interface_valid": config.default_interface in {"SWD", "JTAG"},
            "svd_configured": bool(config.svd_dir),
            "svd_path_exists": bool(svd_path and svd_path.exists()),
            "svd_loaded": svd_manager.is_available(),
            "patch_configured": bool(config.patch_dir),
            "patch_manifest_exists": bool(patch_manifest and patch_manifest.exists()),
            "patch_loaded": device_patch_manager.patch_count > 0,
            "gdb_server_binary_available": bool(gdb_server_path),
            "semantic_enabled": config.semantic_enabled,
        }

        warnings = []
        if not checks["svd_loaded"]:
            warnings.append("SVD resources are not loaded; SVD register parsing tools will be unavailable")
        if not checks["patch_loaded"]:
            warnings.append("No private patch is loaded; private chip-name matching will be unavailable")
        if not checks["gdb_server_binary_available"]:
            warnings.append("JLinkGDBServer.exe was not found; GDB server tools may be unavailable")

        recommendations = []
        if not checks["svd_loaded"]:
            recommendations.append("Set JLINK_SVD_DIR to an external SVD directory if you need register parsing")
        if not checks["patch_loaded"]:
            recommendations.append("Set JLINK_PATCH_DIR to a private patch/provider directory if you need vendor extensions")
        if config.default_interface == "JTAG":
            recommendations.append("If your target prefers SWD, set JLINK_DEFAULT_INTERFACE=SWD")

        diagnosis = {
            "env_overrides": env_overrides,
            "paths": {
                "svd_path": str(svd_path) if svd_path else None,
                "patch_manifest": str(patch_manifest) if patch_manifest else None,
                "gdb_server_binary": gdb_server_path,
            },
            "checks": checks,
            "warnings": warnings,
            "recommendations": recommendations,
        }

        return {
            "success": True,
            "data": diagnosis,
            "message": "Environment diagnosis completed"
        }
    except Exception as e:
        logger.error(f"Failed to diagnose environment: {e}")
        return {
            "success": False,
            "data": None,
            "error": str(e),
            "message": "Failed to diagnose environment"
        }
