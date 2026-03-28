"""Tests for lgtv.commands.media module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.media import media
from lgtv.tv import TVConnectionError, TVAuthenticationError


@pytest.fixture
def runner():
    """Click CLI runner."""
    return CliRunner()


class TestMediaPlay:
    """Tests for media play command."""

    def test_media_play_success(self, runner, sample_config):
        """media play starts playback."""
        with patch("lgtv.commands.media.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(media, ["play"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.play.assert_called_once()
            assert "Playback started" in result.output

    def test_media_play_connection_error(self, runner, sample_config):
        """media play handles connection errors."""
        with patch("lgtv.commands.media.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(media, ["play"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output

    def test_media_play_auth_error(self, runner, sample_config):
        """media play handles authentication errors."""
        with patch("lgtv.commands.media.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(media, ["play"], obj=sample_config)

            assert result.exit_code != 0
            assert "Auth failed" in result.output

    def test_media_play_with_tv_option(self, runner, sample_config):
        """media play accepts --tv option."""
        with patch("lgtv.commands.media.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(media, ["play", "--tv", "bedroom"], obj=sample_config)

            assert result.exit_code == 0
            MockController.assert_called_with(sample_config, tv_name="bedroom", ip=None)


class TestMediaPause:
    """Tests for media pause command."""

    def test_media_pause_success(self, runner, sample_config):
        """media pause pauses playback."""
        with patch("lgtv.commands.media.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(media, ["pause"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.pause.assert_called_once()
            assert "Playback paused" in result.output

    def test_media_pause_connection_error(self, runner, sample_config):
        """media pause handles connection errors."""
        with patch("lgtv.commands.media.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(media, ["pause"], obj=sample_config)

            assert result.exit_code != 0


class TestMediaStop:
    """Tests for media stop command."""

    def test_media_stop_success(self, runner, sample_config):
        """media stop stops playback."""
        with patch("lgtv.commands.media.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(media, ["stop"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.stop.assert_called_once()
            assert "Playback stopped" in result.output


class TestMediaRewind:
    """Tests for media rewind command."""

    def test_media_rewind_success(self, runner, sample_config):
        """media rewind rewinds playback."""
        with patch("lgtv.commands.media.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(media, ["rewind"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.rewind.assert_called_once()
            assert "Rewinding" in result.output


class TestMediaForward:
    """Tests for media forward command."""

    def test_media_forward_success(self, runner, sample_config):
        """media forward fast-forwards playback."""
        with patch("lgtv.commands.media.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(media, ["forward"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.media.fast_forward.assert_called_once()
            assert "Fast forwarding" in result.output

    def test_media_forward_connection_error(self, runner, sample_config):
        """media forward handles connection errors."""
        with patch("lgtv.commands.media.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(media, ["forward"], obj=sample_config)

            assert result.exit_code != 0


class TestMediaWithIpOption:
    """Tests for media commands with --ip option."""

    def test_media_play_with_ip(self, runner, sample_config):
        """media play accepts --ip option."""
        with patch("lgtv.commands.media.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(media, ["play", "--ip", "192.168.1.200"], obj=sample_config)

            assert result.exit_code == 0
            MockController.assert_called_with(sample_config, tv_name=None, ip="192.168.1.200")
