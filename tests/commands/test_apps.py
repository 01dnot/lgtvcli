"""Tests for lgtv.commands.apps module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.apps import app
from lgtv.tv import TVConnectionError, TVAuthenticationError


@pytest.fixture
def runner():
    """Click CLI runner."""
    return CliRunner()


@pytest.fixture
def sample_apps():
    """Sample app list."""
    return [
        {"id": "netflix", "title": "Netflix"},
        {"id": "youtube.leanback.v4", "title": "YouTube"},
        {"id": "com.webos.app.browser", "title": "Web Browser"},
        {"id": "amazon.prime", "title": "Prime Video"},
    ]


class TestAppList:
    """Tests for app list command."""

    def test_app_list_success(self, runner, sample_config, sample_apps):
        """app list shows installed applications."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "Netflix" in result.output
            assert "YouTube" in result.output
            assert "Web Browser" in result.output
            assert "4" in result.output  # App count

    def test_app_list_empty(self, runner, sample_config):
        """app list handles no apps."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = []
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "No applications found" in result.output

    def test_app_list_sorted(self, runner, sample_config, sample_apps):
        """app list sorts apps alphabetically."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["list"], obj=sample_config)

            # Netflix should appear before YouTube due to alphabetical sorting
            netflix_pos = result.output.find("Netflix")
            youtube_pos = result.output.find("YouTube")
            assert netflix_pos < youtube_pos

    def test_app_list_connection_error(self, runner, sample_config):
        """app list handles connection errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output


class TestAppLaunch:
    """Tests for app launch command."""

    def test_app_launch_success(self, runner, sample_config, sample_apps):
        """app launch launches app by name."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "Netflix"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.app.launch.assert_called_once()
            assert "Launched" in result.output
            assert "Netflix" in result.output

    def test_app_launch_case_insensitive(self, runner, sample_config, sample_apps):
        """app launch is case-insensitive."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "NETFLIX"], obj=sample_config)

            assert result.exit_code == 0
            assert "Launched" in result.output

    def test_app_launch_partial_match(self, runner, sample_config, sample_apps):
        """app launch matches partial names."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "prime"], obj=sample_config)

            assert result.exit_code == 0
            assert "Prime Video" in result.output

    def test_app_launch_not_found(self, runner, sample_config, sample_apps):
        """app launch fails when app not found."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "Nonexistent"], obj=sample_config)

            assert result.exit_code != 0
            assert "not found" in result.output

    def test_app_launch_empty_app_list(self, runner, sample_config):
        """app launch fails when no apps available."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = []
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "Netflix"], obj=sample_config)

            assert result.exit_code != 0
            assert "Could not retrieve app list" in result.output


class TestAppCurrent:
    """Tests for app current command."""

    def test_app_current_success(self, runner, sample_config):
        """app current shows foreground application."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.return_value = {
                "appId": "netflix",
                "title": "Netflix",
                "windowId": "win123",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "Netflix" in result.output
            assert "netflix" in result.output

    def test_app_current_with_window_id(self, runner, sample_config):
        """app current shows window ID if available."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.return_value = {
                "appId": "youtube",
                "title": "YouTube",
                "windowId": "window_456",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "window_456" in result.output

    def test_app_current_none(self, runner, sample_config):
        """app current handles no current app."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.return_value = None
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "No application currently running" in result.output


class TestAppClose:
    """Tests for app close command."""

    def test_app_close_success(self, runner, sample_config):
        """app close closes application by ID."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["close", "netflix"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.app.close.assert_called_once_with({"id": "netflix"})
            assert "Closed application" in result.output

    def test_app_close_connection_error(self, runner, sample_config):
        """app close handles connection errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(app, ["close", "netflix"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output

    def test_app_close_auth_error(self, runner, sample_config):
        """app close handles auth errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(app, ["close", "netflix"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_app_close_generic_error(self, runner, sample_config):
        """app close handles generic errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.close.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["close", "netflix"], obj=sample_config)

            assert "Failed to close" in result.output


class TestAppListEdgeCases:
    """Tests for app list edge cases."""

    def test_app_list_auth_error(self, runner, sample_config):
        """app list handles auth errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_app_list_generic_error(self, runner, sample_config):
        """app list handles generic errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert "Failed to list" in result.output

    def test_app_list_with_data_attribute(self, runner, sample_config):
        """app list handles apps with .data attribute."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_app = MagicMock()
            mock_app.data = {"id": "test_app", "title": "Test App"}
            mock_controller.app.list_apps.return_value = [mock_app]
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "Test App" in result.output

    def test_app_list_with_unknown_object_type(self, runner, sample_config):
        """app list handles unknown object types."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_app = MagicMock(spec=[])  # No .data attribute
            mock_app.id = "my_app"
            mock_app.title = "My App"
            mock_controller.app.list_apps.return_value = [mock_app]
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert result.exit_code == 0
            assert "My App" in result.output

    def test_app_list_with_appId_attribute(self, runner, sample_config):
        """app list handles objects with appId attribute."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_app = MagicMock(spec=[])
            mock_app.appId = "my_app_id"
            mock_app.name = "App Name"
            mock_controller.app.list_apps.return_value = [mock_app]
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["list"], obj=sample_config)

            assert result.exit_code == 0


class TestAppLaunchEdgeCases:
    """Tests for app launch edge cases."""

    def test_app_launch_auth_error(self, runner, sample_config):
        """app launch handles auth errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(app, ["launch", "Netflix"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_app_launch_generic_error(self, runner, sample_config, sample_apps):
        """app launch handles generic errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            mock_controller.app.launch.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "Netflix"], obj=sample_config)

            assert "Failed to launch" in result.output

    def test_app_launch_with_debug(self, runner, sample_config, sample_apps):
        """app launch --debug shows debug info."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = sample_apps
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "Netflix", "--debug"], obj=sample_config)

            assert result.exit_code == 0
            assert "DEBUG:" in result.output

    def test_app_launch_debug_with_data_attr(self, runner, sample_config):
        """app launch --debug shows .data info."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_app = MagicMock()
            mock_app.data = {"id": "netflix", "title": "Netflix"}
            mock_controller.app.list_apps.return_value = [mock_app]
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "Netflix", "--debug"], obj=sample_config)

            assert "DEBUG:" in result.output

    def test_app_launch_app_no_id(self, runner, sample_config):
        """app launch handles app without ID."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.list_apps.return_value = [{"title": "Netflix"}]  # No id
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["launch", "Netflix"], obj=sample_config)

            assert "has no ID" in result.output


class TestAppCurrentEdgeCases:
    """Tests for app current edge cases."""

    def test_app_current_auth_error(self, runner, sample_config):
        """app current handles auth errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_app_current_generic_error(self, runner, sample_config):
        """app current handles generic errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.app.get_current.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert "Failed to get current" in result.output

    def test_app_current_with_data_attribute(self, runner, sample_config):
        """app current handles response with .data attribute."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_response = MagicMock()
            mock_response.data = {
                "appId": "youtube",
                "title": "YouTube",
                "windowId": "win123"
            }
            mock_controller.app.get_current.return_value = mock_response
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "YouTube" in result.output
            assert "win123" in result.output

    def test_app_current_with_attributes(self, runner, sample_config):
        """app current handles response with direct attributes."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)

            mock_response = MagicMock(spec=[])
            mock_response.title = "Spotify"
            mock_response.appId = "spotify"
            mock_response.windowId = None
            mock_controller.app.get_current.return_value = mock_response
            MockController.return_value = mock_controller

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert result.exit_code == 0
            assert "Spotify" in result.output

    def test_app_current_connection_error(self, runner, sample_config):
        """app current handles connection errors."""
        with patch("lgtv.commands.apps.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(app, ["current"], obj=sample_config)

            assert "Connection failed" in result.output
