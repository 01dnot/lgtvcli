"""Tests for lgtv.commands.volume module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.volume import volume, audio
from lgtv.tv import TVConnectionError, TVAuthenticationError


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


class TestVolumeAuthErrors:
    """Tests for authentication error handling."""

    def test_volume_up_auth_error(self, runner, sample_config):
        """volume up handles authentication errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(volume, ["up"], obj=sample_config)

            assert result.exit_code != 0
            assert "Auth failed" in result.output

    def test_volume_down_auth_error(self, runner, sample_config):
        """volume down handles authentication errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(volume, ["down"], obj=sample_config)

            assert result.exit_code != 0

    def test_volume_set_auth_error(self, runner, sample_config):
        """volume set handles authentication errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(volume, ["set", "50"], obj=sample_config)

            assert result.exit_code != 0

    def test_volume_mute_auth_error(self, runner, sample_config):
        """volume mute handles authentication errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code != 0


class TestVolumeGenericErrors:
    """Tests for generic error handling."""

    def test_volume_up_generic_error(self, runner, sample_config):
        """volume up handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.volume_up.side_effect = Exception("Something broke")
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["up"], obj=sample_config)

            assert "Failed to increase volume" in result.output

    def test_volume_down_generic_error(self, runner, sample_config):
        """volume down handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.volume_down.side_effect = Exception("Something broke")
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["down"], obj=sample_config)

            assert "Failed to decrease volume" in result.output

    def test_volume_set_generic_error(self, runner, sample_config):
        """volume set handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.set_volume.side_effect = Exception("Something broke")
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["set", "50"], obj=sample_config)

            assert "Failed to set volume" in result.output

    def test_volume_mute_generic_error(self, runner, sample_config):
        """volume mute handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.side_effect = Exception("Something broke")
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert "Failed to toggle mute" in result.output

    def test_volume_status_generic_error(self, runner, sample_config):
        """volume status handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.side_effect = Exception("Something broke")
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["status"], obj=sample_config)

            assert "Failed to get volume status" in result.output


class TestVolumeMuteEdgeCases:
    """Tests for mute edge cases."""

    def test_volume_mute_with_data_attribute_nested(self, runner, sample_config):
        """volume mute handles object with data.volumeStatus."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            # Create response object with .data attribute containing volumeStatus
            mock_response = MagicMock()
            mock_response.data = {"volumeStatus": {"muteStatus": True}}
            mock_controller.media.get_volume.return_value = mock_response
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.mute.assert_called_once_with(False)

    def test_volume_mute_with_data_attribute_flat(self, runner, sample_config):
        """volume mute handles object with data.muted."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_response = MagicMock()
            mock_response.data = {"muted": False}
            mock_controller.media.get_volume.return_value = mock_response
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.mute.assert_called_once_with(True)

    def test_volume_mute_with_none_volume_info(self, runner, sample_config):
        """volume mute handles None volume info."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = None
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code == 0
            # With None, current_mute defaults to False, so it will mute
            mock_controller.media.mute.assert_called_once_with(True)

    def test_volume_mute_with_unknown_type(self, runner, sample_config):
        """volume mute handles unknown response type."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            # Return something that's not a dict and doesn't have .data
            mock_controller.media.get_volume.return_value = "unknown"
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["mute"], obj=sample_config)

            assert result.exit_code == 0


class TestVolumeStatusDebug:
    """Tests for volume status debug mode."""

    def test_volume_status_debug(self, runner, sample_config):
        """volume status --debug shows debug info."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = {"volume": 45, "muted": False}
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["status", "--debug"], obj=sample_config)

            assert result.exit_code == 0
            assert "DEBUG:" in result.output
            assert "Type:" in result.output

    def test_volume_status_debug_with_data_attr(self, runner, sample_config):
        """volume status --debug shows .data attribute."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_response = MagicMock()
            mock_response.data = {"volume": 45}
            mock_controller.media.get_volume.return_value = mock_response
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["status", "--debug"], obj=sample_config)

            assert result.exit_code == 0
            assert ".data:" in result.output

    def test_volume_status_none_volume(self, runner, sample_config):
        """volume status handles None volume info."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_volume.return_value = None
            MockController.return_value = mock_controller

            result = runner.invoke(volume, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "Could not retrieve" in result.output

    def test_volume_status_connection_error(self, runner, sample_config):
        """volume status handles connection errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(volume, ["status"], obj=sample_config)

            assert "Connection failed" in result.output

    def test_volume_status_auth_error(self, runner, sample_config):
        """volume status handles auth errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(volume, ["status"], obj=sample_config)

            assert "Auth failed" in result.output


class TestAudioErrors:
    """Tests for audio error handling."""

    def test_audio_list_connection_error(self, runner, sample_config):
        """audio list handles connection errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert "Connection failed" in result.output

    def test_audio_list_auth_error(self, runner, sample_config):
        """audio list handles auth errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_audio_list_generic_error(self, runner, sample_config):
        """audio list handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.list_audio_output_sources.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert "Failed to list" in result.output

    def test_audio_set_connection_error(self, runner, sample_config):
        """audio set handles connection errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(audio, ["set", "tv_speaker"], obj=sample_config)

            assert "Connection failed" in result.output

    def test_audio_set_auth_error(self, runner, sample_config):
        """audio set handles auth errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(audio, ["set", "tv_speaker"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_audio_set_generic_error(self, runner, sample_config):
        """audio set handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.set_audio_output.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["set", "tv_speaker"], obj=sample_config)

            assert "Failed to set" in result.output

    def test_audio_status_connection_error(self, runner, sample_config):
        """audio status handles connection errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert "Connection failed" in result.output

    def test_audio_status_auth_error(self, runner, sample_config):
        """audio status handles auth errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_audio_status_generic_error(self, runner, sample_config):
        """audio status handles generic errors."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_audio_output.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert "Failed to get" in result.output

    def test_audio_status_none_output(self, runner, sample_config):
        """audio status handles None output."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.media.get_audio_output.return_value = None
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert "Could not retrieve" in result.output


class TestAudioListEdgeCases:
    """Tests for audio list edge cases."""

    def test_audio_list_with_data_attribute(self, runner, sample_config):
        """audio list handles sources with .data attribute."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_source = MagicMock()
            mock_source.data = {"soundOutput": "hdmi_arc"}
            mock_controller.media.list_audio_output_sources.return_value = [mock_source]

            mock_current = MagicMock()
            mock_current.data = {"soundOutput": "hdmi_arc"}
            mock_controller.media.get_audio_output.return_value = mock_current
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "hdmi_arc" in result.output

    def test_audio_list_with_soundOutput_attribute(self, runner, sample_config):
        """audio list handles sources with soundOutput attribute."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_source = MagicMock(spec=[])
            mock_source.soundOutput = "optical"
            mock_controller.media.list_audio_output_sources.return_value = [mock_source]
            mock_controller.media.get_audio_output.return_value = {"soundOutput": "tv_speaker"}
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "optical" in result.output

    def test_audio_list_unknown_source_type(self, runner, sample_config):
        """audio list handles unknown source types."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            # Return a string source (unusual but possible)
            mock_controller.media.list_audio_output_sources.return_value = ["speaker1"]
            mock_controller.media.get_audio_output.return_value = None
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["list"], obj=sample_config)

            assert result.exit_code == 0


class TestAudioStatusEdgeCases:
    """Tests for audio status edge cases."""

    def test_audio_status_with_data_attribute(self, runner, sample_config):
        """audio status handles response with .data attribute."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_output = MagicMock()
            mock_output.data = {"soundOutput": "hdmi_arc"}
            mock_controller.media.get_audio_output.return_value = mock_output
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "hdmi_arc" in result.output

    def test_audio_status_with_soundOutput_attribute(self, runner, sample_config):
        """audio status handles response with soundOutput attribute."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_output = MagicMock(spec=[])
            mock_output.soundOutput = "optical"
            mock_controller.media.get_audio_output.return_value = mock_output
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "optical" in result.output

    def test_audio_status_unknown_type(self, runner, sample_config):
        """audio status handles unknown response types."""
        with patch("lgtv.commands.volume.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            # Return a plain string
            mock_controller.media.get_audio_output.return_value = "some_output"
            MockController.return_value = mock_controller

            result = runner.invoke(audio, ["status"], obj=sample_config)

            assert result.exit_code == 0
