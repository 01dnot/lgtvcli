"""Tests for lgtv.commands.volume module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.volume import volume, audio
from lgtv.tv import TVConnectionError


@pytest.fixture
def runner():
    """Click CLI runner."""
    return CliRunner()


class TestVolumeUp:
    """Tests for volume up command."""

    def test_volume_up_success(self, runner, sample_config):
        """volume up increases volume."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 26, "muted": False}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["up"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.volume_up.assert_called_once()
            assert "Volume increased" in result.output

    def test_volume_up_shows_level(self, runner, sample_config):
        """volume up shows current volume level."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 50, "muted": False}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["up"], obj=sample_config)

            assert "Volume: 50" in result.output

    def test_volume_up_connection_error(self, runner, sample_config):
        """volume up handles connection errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(volume, ["up"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output


class TestVolumeDown:
    """Tests for volume down command."""

    def test_volume_down_success(self, runner, sample_config):
        """volume down decreases volume."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 24, "muted": False}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["down"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.volume_down.assert_called_once()
            assert "Volume decreased" in result.output


class TestVolumeSet:
    """Tests for volume set command."""

    def test_volume_set_success(self, runner, sample_config):
        """volume set sets specific volume level."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["set", "50"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.set_volume.assert_called_once_with(50)
            assert "Volume set to 50" in result.output

    def test_volume_set_min(self, runner, sample_config):
        """volume set accepts 0."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["set", "0"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.set_volume.assert_called_once_with(0)

    def test_volume_set_max(self, runner, sample_config):
        """volume set accepts 100."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["set", "100"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.set_volume.assert_called_once_with(100)

    def test_volume_set_out_of_range(self, runner, sample_config):
        """volume set rejects out-of-range values."""
        result = runner.invoke(volume, ["set", "150"], obj=sample_config)

        assert result.exit_code != 0
        assert "150" in result.output or "range" in result.output.lower()


class TestVolumeMute:
    """Tests for volume mute command."""

    def test_volume_mute_toggle_on(self, runner, sample_config):
        """volume mute toggles mute on when currently unmuted."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 25, "muted": False}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.mute.assert_called_once_with(True)
            assert "Muted" in result.output

    def test_volume_mute_toggle_off(self, runner, sample_config):
        """volume mute toggles mute off when currently muted."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 25, "muted": True}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.mute.assert_called_once_with(False)
            assert "Unmuted" in result.output

    def test_volume_mute_nested_volume_status(self, runner, sample_config):
        """volume mute handles nested volumeStatus structure."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {
                "volumeStatus": {"volume": 25, "muteStatus": False}
            }
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.mute.assert_called_once_with(True)


class TestVolumeStatus:
    """Tests for volume status command."""

    def test_volume_status_success(self, runner, sample_config):
        """volume status shows current volume."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 45, "muted": False}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "45" in result.output
            assert "UNMUTED" in result.output

    def test_volume_status_muted(self, runner, sample_config):
        """volume status shows muted state."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 45, "muted": True}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "MUTED" in result.output


class TestAudioList:
    """Tests for audio list command."""

    def test_audio_list_success(self, runner, sample_config):
        """audio list shows available audio outputs."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.list_audio_output_sources.return_value = [
                {"soundOutput": "tv_speaker"},
                {"soundOutput": "external_arc"},
            ]
            mock_controller.media.get_audio_output.return_value = {"soundOutput": "tv_speaker"}
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "tv_speaker" in result.output
            assert "external_arc" in result.output
            assert "(current)" in result.output

    def test_audio_list_empty(self, runner, sample_config):
        """audio list handles no sources available."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.list_audio_output_sources.return_value = []
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "No audio output sources" in result.output


class TestAudioSet:
    """Tests for audio set command."""

    def test_audio_set_success(self, runner, sample_config):
        """audio set changes audio output."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["set", "external_arc"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.set_audio_output.assert_called_once_with("external_arc")
            assert "external_arc" in result.output


class TestAudioStatus:
    """Tests for audio status command."""

    def test_audio_status_success(self, runner, sample_config):
        """audio status shows current output."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_audio_output.return_value = {"soundOutput": "external_arc"}
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "external_arc" in result.output
