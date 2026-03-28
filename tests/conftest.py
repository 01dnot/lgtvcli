"""Shared fixtures for lgtvcli tests."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from click.testing import CliRunner

from lgtv.config import Config


# ============================================================================
# Configuration Fixtures
# ============================================================================

@pytest.fixture
def temp_config_dir(tmp_path):
    """Create an isolated temporary directory for config tests."""
    config_dir = tmp_path / ".config" / "lgtv"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


@pytest.fixture
def temp_config_path(temp_config_dir):
    """Return path to a temp config file."""
    return str(temp_config_dir / "config.json")


@pytest.fixture
def empty_config(temp_config_path):
    """Create an empty Config instance with isolated config file."""
    return Config(config_path=temp_config_path)


@pytest.fixture
def sample_tv_data():
    """Sample TV configuration data."""
    return {
        "living_room": {
            "name": "living_room",
            "ip": "192.168.1.100",
            "mac": "AA:BB:CC:DD:EE:FF",
            "key": "abc123key",
            "model": "OLED65C1",
        },
        "bedroom": {
            "name": "bedroom",
            "ip": "192.168.1.101",
            "mac": "11:22:33:44:55:66",
            "key": "xyz789key",
            "model": "OLED55B1",
        },
    }


@pytest.fixture
def sample_config(temp_config_path, sample_tv_data):
    """Create a Config instance pre-populated with test TV data."""
    # Pre-populate the config file
    config_data = {
        "default_tv": "living_room",
        "tvs": sample_tv_data,
    }
    with open(temp_config_path, "w") as f:
        json.dump(config_data, f)

    return Config(config_path=temp_config_path)


# ============================================================================
# Click Testing Fixtures
# ============================================================================

@pytest.fixture
def cli_runner():
    """Click CliRunner instance for testing CLI commands."""
    return CliRunner()


# ============================================================================
# PyWebOSTV Mock Fixtures
# ============================================================================

@pytest.fixture
def mock_webos_client():
    """Mock WebOSClient from PyWebOSTV."""
    with patch("lgtv.tv.WebOSClient") as MockClient:
        client_instance = MagicMock()
        client_instance.connect = MagicMock()
        client_instance.close = MagicMock()

        # Register returns a generator yielding status
        def register_side_effect(store):
            store["client_key"] = "test_key_123"
            yield MockClient.REGISTERED

        client_instance.register = MagicMock(side_effect=register_side_effect)

        MockClient.return_value = client_instance
        MockClient.PROMPTED = 0
        MockClient.REGISTERED = 1

        yield MockClient


@pytest.fixture
def mock_system_control():
    """Mock SystemControl from PyWebOSTV."""
    mock = MagicMock()
    mock.info.return_value = {
        "modelName": "OLED65C1",
        "sdkVersion": "7.0.0",
        "firmwareRevision": "1.0.0",
    }
    mock.power_off = MagicMock()
    mock.screen_off = MagicMock()
    mock.screen_on = MagicMock()
    mock.notify = MagicMock()
    return mock


@pytest.fixture
def mock_media_control():
    """Mock MediaControl from PyWebOSTV."""
    mock = MagicMock()
    mock.get_volume.return_value = {
        "volumeStatus": {
            "volume": 25,
            "muteStatus": False,
        }
    }
    mock.volume_up = MagicMock()
    mock.volume_down = MagicMock()
    mock.set_volume = MagicMock()
    mock.mute = MagicMock()
    mock.play = MagicMock()
    mock.pause = MagicMock()
    mock.stop = MagicMock()
    mock.rewind = MagicMock()
    mock.fast_forward = MagicMock()
    mock.list_audio_output_sources.return_value = [
        {"soundOutput": "tv_speaker"},
        {"soundOutput": "external_arc"},
    ]
    mock.get_audio_output.return_value = {"soundOutput": "tv_speaker"}
    mock.set_audio_output = MagicMock()
    return mock


@pytest.fixture
def mock_app_control():
    """Mock ApplicationControl from PyWebOSTV."""
    mock = MagicMock()
    mock.list_apps.return_value = [
        {"id": "netflix", "title": "Netflix"},
        {"id": "youtube.leanback.v4", "title": "YouTube"},
        {"id": "com.webos.app.browser", "title": "Web Browser"},
    ]
    mock.get_current.return_value = {
        "appId": "netflix",
        "title": "Netflix",
        "windowId": "win123",
    }
    mock.launch = MagicMock()
    mock.close = MagicMock()
    return mock


@pytest.fixture
def mock_input_control():
    """Mock InputControl from PyWebOSTV."""
    mock = MagicMock()
    mock.connect_input = MagicMock()
    mock.disconnect_input = MagicMock()
    mock.home = MagicMock()
    mock.back = MagicMock()
    mock.up = MagicMock()
    mock.down = MagicMock()
    mock.left = MagicMock()
    mock.right = MagicMock()
    mock.ok = MagicMock()
    mock.menu = MagicMock()
    mock.info = MagicMock()
    mock.exit = MagicMock()
    mock.dash = MagicMock()
    mock.red = MagicMock()
    mock.green = MagicMock()
    mock.yellow = MagicMock()
    mock.blue = MagicMock()
    mock.asterisk = MagicMock()
    mock.cc = MagicMock()
    mock.num_0 = MagicMock()
    mock.num_1 = MagicMock()
    mock.num_2 = MagicMock()
    mock.num_3 = MagicMock()
    mock.num_4 = MagicMock()
    mock.num_5 = MagicMock()
    mock.num_6 = MagicMock()
    mock.num_7 = MagicMock()
    mock.num_8 = MagicMock()
    mock.num_9 = MagicMock()
    mock.type = MagicMock()
    mock.move = MagicMock()
    mock.click = MagicMock()
    return mock


@pytest.fixture
def mock_tv_control():
    """Mock TvControl from PyWebOSTV."""
    mock = MagicMock()
    mock.channel_up = MagicMock()
    mock.channel_down = MagicMock()
    mock.set_channel_with_id = MagicMock()
    mock.get_current_channel.return_value = {
        "channelNumber": "5",
        "channelName": "NBC",
        "channelId": "ch_5",
    }
    mock.get_current_program.return_value = {
        "programName": "Evening News",
        "startTime": "18:00",
        "endTime": "18:30",
    }
    mock.channel_list.return_value = [
        {"channelNumber": "1", "channelName": "ABC", "channelId": "ch_1"},
        {"channelNumber": "5", "channelName": "NBC", "channelId": "ch_5"},
        {"channelNumber": "10", "channelName": "CBS", "channelId": "ch_10"},
    ]
    return mock


@pytest.fixture
def mock_source_control():
    """Mock SourceControl from PyWebOSTV."""
    mock = MagicMock()
    mock.list_sources.return_value = [
        {"id": "HDMI_1", "label": "HDMI 1", "connected": True},
        {"id": "HDMI_2", "label": "HDMI 2", "connected": False},
        {"id": "HDMI_3", "label": "HDMI 3", "connected": True},
    ]
    mock.set_source = MagicMock()
    return mock


@pytest.fixture
def mock_tv_controller(
    sample_config,
    mock_webos_client,
    mock_system_control,
    mock_media_control,
    mock_app_control,
    mock_input_control,
    mock_tv_control,
    mock_source_control,
):
    """Fully mocked TVController for command tests."""
    with patch("lgtv.tv.WebOSClient", mock_webos_client), \
         patch("lgtv.tv.SystemControl", return_value=mock_system_control), \
         patch("lgtv.tv.MediaControl", return_value=mock_media_control), \
         patch("lgtv.tv.ApplicationControl", return_value=mock_app_control), \
         patch("lgtv.tv.InputControl", return_value=mock_input_control), \
         patch("lgtv.tv.TvControl", return_value=mock_tv_control), \
         patch("lgtv.tv.SourceControl", return_value=mock_source_control):

        from lgtv.tv import TVController
        controller = TVController(sample_config, tv_name="living_room")

        # Expose the mocks for assertions
        controller._mock_system = mock_system_control
        controller._mock_media = mock_media_control
        controller._mock_app = mock_app_control
        controller._mock_input = mock_input_control
        controller._mock_tv = mock_tv_control
        controller._mock_source = mock_source_control

        yield controller


@pytest.fixture
def mock_tv_controller_factory(
    sample_config,
    mock_system_control,
    mock_media_control,
    mock_app_control,
    mock_input_control,
    mock_tv_control,
    mock_source_control,
):
    """Factory fixture that patches TVController for command tests.

    Use this when you need to test commands that instantiate TVController internally.
    """
    def _create_mock():
        mock_controller = MagicMock()
        mock_controller.system = mock_system_control
        mock_controller.media = mock_media_control
        mock_controller.app = mock_app_control
        mock_controller.input = mock_input_control
        mock_controller.tv = mock_tv_control
        mock_controller.source = mock_source_control
        mock_controller.ip = "192.168.1.100"
        mock_controller.tv_name = "living_room"
        mock_controller.disconnect = MagicMock()
        mock_controller.__enter__ = MagicMock(return_value=mock_controller)
        mock_controller.__exit__ = MagicMock(return_value=False)
        return mock_controller

    return _create_mock


# ============================================================================
# Discovery Fixtures
# ============================================================================

@pytest.fixture
def mock_socket():
    """Mock socket module for SSDP discovery tests."""
    with patch("lgtv.discovery.socket") as mock:
        sock_instance = MagicMock()
        mock.socket.return_value = sock_instance
        mock.AF_INET = 2
        mock.SOCK_DGRAM = 2
        mock.IPPROTO_UDP = 17
        mock.inet_ntoa = lambda x: ".".join(str(b) for b in x)
        mock.gaierror = OSError
        yield mock, sock_instance


@pytest.fixture
def mock_zeroconf():
    """Mock Zeroconf for mDNS discovery tests."""
    with patch("lgtv.discovery.Zeroconf") as MockZeroconf, \
         patch("lgtv.discovery.ServiceBrowser") as MockBrowser:
        zc_instance = MagicMock()
        MockZeroconf.return_value = zc_instance
        yield MockZeroconf, MockBrowser, zc_instance


# ============================================================================
# Wake-on-LAN Fixtures
# ============================================================================

@pytest.fixture
def mock_wol():
    """Mock wakeonlan.send_magic_packet."""
    with patch("lgtv.utils.send_magic_packet") as mock:
        yield mock
