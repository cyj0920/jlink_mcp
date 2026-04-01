"""Unit tests for debug resume semantics and auto chip detection behavior."""

from __future__ import annotations

import importlib
from unittest.mock import Mock

import pytest

from jlink_mcp.jlink_manager import COMMON_AUTO_DETECT_CHIPS, jlink_manager
from jlink_mcp.models.device import TargetInterface
from jlink_mcp.tools.debug import run_cpu

jlink_manager_module = importlib.import_module("jlink_mcp.jlink_manager")


@pytest.fixture
def preserve_jlink_manager_state():
    """Preserve singleton state for tests / 为测试保存单例状态."""
    manager = jlink_manager
    snapshot = {
        "_jlink": manager._jlink,
        "_connected": manager._connected,
        "_device_serial": manager._device_serial,
        "_target_interface": manager._target_interface,
        "_target_connected": manager._target_connected,
    }
    manager._cleanup()
    try:
        yield manager
    finally:
        manager._cleanup()
        manager._jlink = snapshot["_jlink"]
        manager._connected = snapshot["_connected"]
        manager._device_serial = snapshot["_device_serial"]
        manager._target_interface = snapshot["_target_interface"]
        manager._target_connected = snapshot["_target_connected"]


@pytest.mark.unit
class TestRunCpuBehavior:
    """Tests for run_cpu semantics / run_cpu 语义测试."""

    def test_run_cpu_resumes_halted_target(self, monkeypatch):
        mock_jlink = Mock()
        mock_jlink.halted.return_value = True
        mock_jlink.restart.return_value = True

        mock_manager = Mock()
        mock_manager.get_jlink.return_value = mock_jlink
        monkeypatch.setattr("jlink_mcp.tools.debug.jlink_manager", mock_manager)

        result = run_cpu()

        assert result["success"] is True
        assert "恢复运行" in result["message"]
        mock_jlink.restart.assert_called_once_with(skip_breakpoints=True)
        mock_jlink.reset.assert_not_called()

    def test_run_cpu_reports_already_running(self, monkeypatch):
        mock_jlink = Mock()
        mock_jlink.halted.return_value = False

        mock_manager = Mock()
        mock_manager.get_jlink.return_value = mock_jlink
        monkeypatch.setattr("jlink_mcp.tools.debug.jlink_manager", mock_manager)

        result = run_cpu()

        assert result["success"] is True
        assert "已在运行" in result["message"]
        mock_jlink.restart.assert_not_called()


@pytest.mark.unit
class TestAutoChipDetectionBehavior:
    """Tests for chip_name auto-detect handling / chip_name 自动检测行为测试."""

    @pytest.mark.parametrize("chip_name", [None, "auto", "AUTO", "auto-detect", "  auto  "])
    def test_connect_treats_auto_marker_as_autodetect(self, monkeypatch, preserve_jlink_manager_state, chip_name):
        mock_jlink = Mock()
        mock_jlink.target_connected.return_value = True
        mock_jlink.serial_number = "12345678"
        mock_jlink.open.return_value = None
        mock_jlink.set_tif.return_value = None

        auto_connect = Mock()
        match_device_name = Mock()

        monkeypatch.setattr(jlink_manager_module.pylink, "JLink", Mock(return_value=mock_jlink))
        monkeypatch.setattr(preserve_jlink_manager_state, "_auto_connect_target", auto_connect)
        monkeypatch.setattr(jlink_manager_module.device_patch_manager, "match_device_name", match_device_name)

        preserve_jlink_manager_state.connect(
            serial_number="12345678",
            interface=TargetInterface.SWD,
            chip_name=chip_name,
        )

        auto_connect.assert_called_once_with()
        match_device_name.assert_not_called()
        mock_jlink.connect.assert_not_called()

    def test_auto_connect_tries_jlink_then_patch_then_common_chip_fallback(self, monkeypatch, preserve_jlink_manager_state):
        mock_jlink = Mock()
        mock_jlink.connect.side_effect = [
            RuntimeError("autodetect failed"),
            RuntimeError("patch 1 failed"),
            RuntimeError("patch 2 failed"),
            None,
        ]
        preserve_jlink_manager_state._jlink = mock_jlink

        monkeypatch.setattr(jlink_manager_module.device_patch_manager, "get_all_device_names", Mock(return_value=["PATCH_A", "PATCH_B"]))

        preserve_jlink_manager_state._auto_connect_target()

        attempted = [call.args[0] for call in mock_jlink.connect.call_args_list]
        assert attempted[:4] == ["", "PATCH_A", "PATCH_B", COMMON_AUTO_DETECT_CHIPS[0]]
