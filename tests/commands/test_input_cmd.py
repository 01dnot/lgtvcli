"""Tests for lgtv.commands.input_cmd module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.input_cmd import input, channel
from lgtv.tv import TVConnectionError, TVAuthenticationError


@pytest.fixture
def runner():
    """Click CLI runner."""
    return CliRunner()


@pytest.fixture
def sample_sources():
    """Sample input sources."""
    return [
        {"id": "HDMI_1", "label": "HDMI 1", "connected": True},
        {"id": "HDMI_2", "label": "HDMI 2", "connected": False},
        {"id": "HDMI_3", "label": "Game Console", "connected": True},
    ]


@pytest.fixture
def sample_channels():
    """Sample TV channels."""
    return [
        {"channelNumber": "1", "channelName": "ABC", "channelId": "ch_1"},
        {"channelNumber": "5", "channelName": "NBC", "channelId": "ch_5"},
        {"channelNumber": "10", "channelName": "CBS", "channelId": "ch_10"},
    ]


class TestInputList:
    """Tests for input list command."""

    def test_input_list_success(self, runner, sample_config, sample_sources):
        """input list shows available sources."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.source.list_sources.return_value = sample_sources
            MockController.return_value = mock_controller

            result = runner.invoke(input, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "HDMI_1" in result.output
            assert "HDMI_2" in result.output
            assert "connected" in result.output

    def test_input_list_empty(self, runner, sample_config):
        """input list handles no sources."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.source.list_sources.return_value = []
            MockController.return_value = mock_controller

            result = runner.invoke(input, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "No input sources found" in result.output

    def test_input_list_connection_error(self, runner, sample_config):
        """input list handles connection errors."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(input, ["list"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output


class TestInputSet:
    """Tests for input set command."""

    def test_input_set_success(self, runner, sample_config):
        """input set switches input source."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(input, ["set", "HDMI_1"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.source.set_source.assert_called_once_with("HDMI_1")
            assert "Switched to input" in result.output
            assert "HDMI_1" in result.output

    def test_input_set_connection_error(self, runner, sample_config):
        """input set handles connection errors."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(input, ["set", "HDMI_1"], obj=sample_config)

            assert result.exit_code != 0


class TestChannelUp:
    """Tests for channel up command."""

    def test_channel_up_success(self, runner, sample_config):
        """channel up goes to next channel."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.get_current_channel.return_value = {
                "channelNumber": "6",
                "channelName": "Fox",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["up"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.tv.channel_up.assert_called_once()
            assert "Channel up" in result.output


class TestChannelDown:
    """Tests for channel down command."""

    def test_channel_down_success(self, runner, sample_config):
        """channel down goes to previous channel."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.get_current_channel.return_value = {
                "channelNumber": "4",
                "channelName": "NBC",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["down"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.tv.channel_down.assert_called_once()
            assert "Channel down" in result.output


class TestChannelSet:
    """Tests for channel set command."""

    def test_channel_set_success(self, runner, sample_config, sample_channels):
        """channel set jumps to specific channel."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.channel_list.return_value = sample_channels
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["set", "5"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.tv.set_channel_with_id.assert_called_once_with("ch_5")
            assert "Switched to channel 5" in result.output

    def test_channel_set_not_found(self, runner, sample_config, sample_channels):
        """channel set fails when channel not found."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.channel_list.return_value = sample_channels
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["set", "999"], obj=sample_config)

            assert result.exit_code != 0
            assert "not found" in result.output

    def test_channel_set_no_channels(self, runner, sample_config):
        """channel set fails when no channels available."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.channel_list.return_value = []
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["set", "5"], obj=sample_config)

            assert result.exit_code != 0
            assert "Could not retrieve channel list" in result.output


class TestChannelList:
    """Tests for channel list command."""

    def test_channel_list_success(self, runner, sample_config, sample_channels):
        """channel list shows available channels."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.channel_list.return_value = sample_channels
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "ABC" in result.output
            assert "NBC" in result.output
            assert "CBS" in result.output
            assert "3" in result.output  # Channel count

    def test_channel_list_empty(self, runner, sample_config):
        """channel list handles no channels."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.channel_list.return_value = []
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "No channels found" in result.output


class TestChannelInfo:
    """Tests for channel info command."""

    def test_channel_info_success(self, runner, sample_config):
        """channel info shows current channel and program."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.get_current_channel.return_value = {
                "channelNumber": "5",
                "channelName": "NBC",
            }
            mock_controller.tv.get_current_program.return_value = {
                "programName": "Evening News",
                "startTime": "18:00",
                "endTime": "18:30",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["info"], obj=sample_config)

            assert result.exit_code == 0
            assert "NBC" in result.output
            assert "5" in result.output
            assert "Evening News" in result.output

    def test_channel_info_not_watching_tv(self, runner, sample_config):
        """channel info handles not watching TV."""
        with patch("lgtv.commands.input_cmd.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.tv.get_current_channel.return_value = None
            MockController.return_value = mock_controller

            result = runner.invoke(channel, ["info"], obj=sample_config)

            assert result.exit_code == 0
            assert "Not watching TV" in result.output
