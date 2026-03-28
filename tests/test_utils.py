"""Tests for lgtv.utils module."""

import pytest
from unittest.mock import MagicMock, patch

from lgtv.utils import (
    error,
    success,
    info,
    warning,
    wake_on_lan,
    format_volume_info,
    format_app_info,
    find_app_by_name,
)


class TestError:
    """Tests for error() function."""

    def test_error_prints_message(self, capsys):
        """error() prints formatted error message."""
        with pytest.raises(SystemExit) as exc_info:
            error("Test error message")

        assert exc_info.value.code == 1
        captured = capsys.readouterr()
        assert "Error: Test error message" in captured.err

    def test_error_custom_exit_code(self, capsys):
        """error() uses custom exit code when provided."""
        with pytest.raises(SystemExit) as exc_info:
            error("Test error", exit_code=2)

        assert exc_info.value.code == 2

    def test_error_zero_exit_code(self, capsys):
        """error() handles exit code 0."""
        with pytest.raises(SystemExit) as exc_info:
            error("Test error", exit_code=0)

        assert exc_info.value.code == 0


class TestSuccess:
    """Tests for success() function."""

    def test_success_prints_message(self, capsys):
        """success() prints message to stdout."""
        success("Operation completed")
        captured = capsys.readouterr()
        assert "Operation completed" in captured.out


class TestInfo:
    """Tests for info() function."""

    def test_info_prints_message(self, capsys):
        """info() prints message to stdout."""
        info("Information message")
        captured = capsys.readouterr()
        assert "Information message" in captured.out


class TestWarning:
    """Tests for warning() function."""

    def test_warning_prints_message(self, capsys):
        """warning() prints formatted warning message."""
        warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning: Warning message" in captured.out


class TestWakeOnLan:
    """Tests for wake_on_lan() function."""

    def test_wake_on_lan_basic(self, mock_wol):
        """wake_on_lan() sends magic packet."""
        wake_on_lan("AA:BB:CC:DD:EE:FF")
        mock_wol.assert_called_once_with("AA:BB:CC:DD:EE:FF")

    def test_wake_on_lan_with_ip(self, mock_wol):
        """wake_on_lan() sends magic packet to specific IP."""
        wake_on_lan("AA:BB:CC:DD:EE:FF", ip="192.168.1.100")
        mock_wol.assert_called_once_with("AA:BB:CC:DD:EE:FF", ip_address="192.168.1.100")

    def test_wake_on_lan_error_handling(self, mock_wol):
        """wake_on_lan() raises RuntimeError on failure."""
        mock_wol.side_effect = Exception("Network error")

        with pytest.raises(RuntimeError, match="Failed to send Wake-on-LAN packet"):
            wake_on_lan("AA:BB:CC:DD:EE:FF")


class TestFormatVolumeInfo:
    """Tests for format_volume_info() function."""

    def test_format_volume_info_dict(self):
        """format_volume_info() handles simple dict."""
        volume_info = {"volume": 50, "muted": False}
        result = format_volume_info(volume_info)
        assert result == "Volume: 50 (UNMUTED)"

    def test_format_volume_info_dict_muted(self):
        """format_volume_info() shows muted status."""
        volume_info = {"volume": 25, "muted": True}
        result = format_volume_info(volume_info)
        assert result == "Volume: 25 (MUTED)"

    def test_format_volume_info_nested_volume_status(self):
        """format_volume_info() handles nested volumeStatus structure."""
        volume_info = {
            "volumeStatus": {
                "volume": 75,
                "muteStatus": False,
            }
        }
        result = format_volume_info(volume_info)
        assert result == "Volume: 75 (UNMUTED)"

    def test_format_volume_info_nested_muted(self):
        """format_volume_info() handles nested muteStatus."""
        volume_info = {
            "volumeStatus": {
                "volume": 30,
                "muteStatus": True,
            }
        }
        result = format_volume_info(volume_info)
        assert result == "Volume: 30 (MUTED)"

    def test_format_volume_info_object_with_data(self):
        """format_volume_info() handles object with .data attribute."""
        mock_obj = MagicMock()
        mock_obj.data = {"volume": 60, "muted": False}
        result = format_volume_info(mock_obj)
        assert result == "Volume: 60 (UNMUTED)"

    def test_format_volume_info_object_with_nested_data(self):
        """format_volume_info() handles object with nested volumeStatus in .data."""
        mock_obj = MagicMock()
        mock_obj.data = {"volumeStatus": {"volume": 40, "muteStatus": True}}
        result = format_volume_info(mock_obj)
        assert result == "Volume: 40 (MUTED)"

    def test_format_volume_info_object_with_attributes(self):
        """format_volume_info() handles object with direct attributes."""
        mock_obj = MagicMock(spec=[])  # No .data attribute
        mock_obj.volume = 55
        mock_obj.muted = False
        result = format_volume_info(mock_obj)
        assert result == "Volume: 55 (UNMUTED)"

    def test_format_volume_info_unknown_format(self):
        """format_volume_info() handles unknown format gracefully."""
        result = format_volume_info("unknown")
        assert result == "Volume: ? (UNMUTED)"

    def test_format_volume_info_mute_status_key(self):
        """format_volume_info() handles muteStatus key in flat dict."""
        volume_info = {"volume": 45, "muteStatus": True}
        result = format_volume_info(volume_info)
        assert result == "Volume: 45 (MUTED)"


class TestFormatAppInfo:
    """Tests for format_app_info() function."""

    def test_format_app_info_basic(self):
        """format_app_info() formats app with id and title."""
        app_info = {"id": "com.webos.app.netflix", "title": "Netflix"}
        result = format_app_info(app_info)
        assert result == "Netflix (com.webos.app.netflix)"

    def test_format_app_info_name_fallback(self):
        """format_app_info() uses 'name' if 'title' is missing."""
        app_info = {"id": "youtube", "name": "YouTube"}
        result = format_app_info(app_info)
        assert result == "YouTube (youtube)"

    def test_format_app_info_missing_id(self):
        """format_app_info() handles missing id."""
        app_info = {"title": "Some App"}
        result = format_app_info(app_info)
        assert result == "Some App ()"

    def test_format_app_info_missing_title_and_name(self):
        """format_app_info() shows 'Unknown' when both title and name are missing."""
        app_info = {"id": "app.id"}
        result = format_app_info(app_info)
        assert result == "Unknown (app.id)"


class TestFindAppByName:
    """Tests for find_app_by_name() function."""

    @pytest.fixture
    def sample_apps(self):
        """Sample list of apps for testing."""
        return [
            {"id": "netflix", "title": "Netflix"},
            {"id": "youtube.leanback.v4", "title": "YouTube"},
            {"id": "com.webos.app.browser", "title": "Web Browser"},
            {"id": "amazon.prime", "title": "Prime Video"},
        ]

    def test_find_app_by_name_exact_match(self, sample_apps):
        """find_app_by_name() returns exact match first."""
        result = find_app_by_name(sample_apps, "Netflix")
        assert result["id"] == "netflix"

    def test_find_app_by_name_case_insensitive(self, sample_apps):
        """find_app_by_name() is case-insensitive."""
        result = find_app_by_name(sample_apps, "NETFLIX")
        assert result["id"] == "netflix"

        result = find_app_by_name(sample_apps, "youtube")
        assert result["id"] == "youtube.leanback.v4"

    def test_find_app_by_name_partial_match(self, sample_apps):
        """find_app_by_name() returns partial match."""
        result = find_app_by_name(sample_apps, "prime")
        assert result["id"] == "amazon.prime"

    def test_find_app_by_name_prefers_exact_over_partial(self):
        """find_app_by_name() prefers exact match over partial."""
        apps = [
            {"id": "youtube.tv", "title": "YouTube TV"},
            {"id": "youtube", "title": "YouTube"},
        ]
        result = find_app_by_name(apps, "YouTube")
        assert result["id"] == "youtube"

    def test_find_app_by_name_not_found(self, sample_apps):
        """find_app_by_name() returns None when app not found."""
        result = find_app_by_name(sample_apps, "Nonexistent App")
        assert result is None

    def test_find_app_by_name_with_objects(self):
        """find_app_by_name() handles objects with .data attribute."""
        mock_app = MagicMock()
        mock_app.data = {"id": "hulu", "title": "Hulu"}
        apps = [mock_app]

        result = find_app_by_name(apps, "Hulu")
        assert result["id"] == "hulu"

    def test_find_app_by_name_with_attribute_objects(self):
        """find_app_by_name() handles objects with direct attributes."""
        mock_app = MagicMock(spec=[])
        mock_app.id = "disney"
        mock_app.title = "Disney+"
        apps = [mock_app]

        result = find_app_by_name(apps, "Disney+")
        assert result["id"] == "disney"

    def test_find_app_by_name_empty_list(self):
        """find_app_by_name() returns None for empty list."""
        result = find_app_by_name([], "Netflix")
        assert result is None

    def test_find_app_by_name_uses_name_field(self):
        """find_app_by_name() falls back to 'name' field."""
        apps = [{"id": "app1", "name": "Application One"}]
        result = find_app_by_name(apps, "Application One")
        assert result["id"] == "app1"

    def test_find_app_by_name_object_uses_appId(self):
        """find_app_by_name() uses appId for objects without id attribute."""
        mock_app = MagicMock(spec=[])
        mock_app.appId = "spotify"
        mock_app.title = "Spotify"
        apps = [mock_app]

        result = find_app_by_name(apps, "Spotify")
        assert result["id"] == "spotify"
