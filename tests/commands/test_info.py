"""Tests for lgtv.commands.info module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.info import info
from lgtv.tv import TVConnectionError, TVAuthenticationError


@pytest.fixture
def runner():
    """Click CLI runner."""
    return CliRunner()


class TestInfoSystem:
    """Tests for info system command."""

    def test_info_system_success(self, runner, sample_config):
        """info system shows system information."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.return_value = {
                "modelName": "OLED65C1",
                "sdkVersion": "7.0.0",
                "firmwareRevision": "1.2.3",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["system"], obj=sample_config)

            assert result.exit_code == 0
            assert "OLED65C1" in result.output
            assert "7.0.0" in result.output

    def test_info_system_firmware_from_version_parts(self, runner, sample_config):
        """info system shows firmware from major.minor version."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.return_value = {
                "modelName": "OLED65C1",
                "sdkVersion": "7.0.0",
                "major_ver": "04",
                "minor_ver": "50",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["system"], obj=sample_config)

            assert result.exit_code == 0
            assert "04.50" in result.output

    def test_info_system_uhd_support(self, runner, sample_config):
        """info system shows UHD support."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.return_value = {
                "modelName": "OLED65C1",
                "sdkVersion": "7.0.0",
                "UHD": "true",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["system"], obj=sample_config)

            assert result.exit_code == 0
            assert "UHD" in result.output

    def test_info_system_connection_error(self, runner, sample_config):
        """info system handles connection errors."""
        with patch("lgtv.commands.info.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(info, ["system"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output

    def test_info_system_auth_error(self, runner, sample_config):
        """info system handles authentication errors."""
        with patch("lgtv.commands.info.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(info, ["system"], obj=sample_config)

            assert result.exit_code != 0
            assert "Auth failed" in result.output

    def test_info_system_unavailable(self, runner, sample_config):
        """info system handles unavailable info."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.return_value = None
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["system"], obj=sample_config)

            assert result.exit_code == 0
            assert "unavailable" in result.output


class TestInfoCurrent:
    """Tests for info current command."""

    def test_info_current_success(self, runner, sample_config):
        """info current shows current TV state."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.return_value = {
                "appId": "netflix",
                "title": "Netflix",
            }
            mock_controller.tv.get_current_channel.return_value = {
                "channelNumber": "5",
                "channelName": "NBC",
            }
            mock_controller.media.get_volume.return_value = {
                "volume": 25,
                "muted": False,
            }
            mock_controller.media.get_audio_output.return_value = {
                "soundOutput": "tv_speaker",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "Netflix" in result.output
            assert "25" in result.output

    def test_info_current_minimal(self, runner, sample_config):
        """info current handles minimal state info."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.return_value = {
                "appId": "com.webos.app.livetv",
                "title": "Live TV",
            }
            mock_controller.tv.get_current_channel.side_effect = Exception("Not in TV mode")
            mock_controller.media.get_volume.return_value = {"volume": 30, "muted": True}
            mock_controller.media.get_audio_output.side_effect = Exception("Not available")
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "Live TV" in result.output
            assert "MUTED" in result.output

    def test_info_current_connection_error(self, runner, sample_config):
        """info current handles connection errors."""
        with patch("lgtv.commands.info.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(info, ["current"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output

    def test_info_current_nested_volume_status(self, runner, sample_config):
        """info current handles nested volumeStatus."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.return_value = {"appId": "netflix"}
            mock_controller.tv.get_current_channel.side_effect = Exception()
            mock_controller.media.get_volume.return_value = {
                "volumeStatus": {"volume": 45, "muteStatus": False}
            }
            mock_controller.media.get_audio_output.side_effect = Exception()
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "45" in result.output

    def test_info_current_with_tv_option(self, runner, sample_config):
        """info current accepts --tv option."""
        with patch("lgtv.commands.info.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.return_value = {"appId": "netflix"}
            mock_controller.tv.get_current_channel.side_effect = Exception()
            mock_controller.media.get_volume.side_effect = Exception()
            mock_controller.media.get_audio_output.side_effect = Exception()
            MockController.return_value = mock_controller

            result = runner.invoke(info, ["current", "--tv", "bedroom"], obj=sample_config)

            assert result.exit_code == 0
            MockController.assert_called_with(sample_config, tv_name="bedroom", ip=None)
