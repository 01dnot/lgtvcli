"""Tests for lgtv.commands.discover_features module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.cli import main
from lgtv.commands.discover_features import discover_features


class TestDiscoverFeatures:
    """Tests for discover_features command."""

    @pytest.fixture
    def cli_runner(self):
        return CliRunner()

    def test_discover_features_shows_services(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features shows available TV services."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {
            "services": [
                {"name": "audio.getVolume", "version": "1.0"},
                {"name": "audio.setVolume", "version": "1.0"},
                {"name": "system.info", "version": "2.0"},
            ]
        }

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features"])

        assert result.exit_code == 0
        assert "3 available services" in result.output

    def test_discover_features_groups_by_category(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features groups services by category."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {
            "services": [
                {"name": "audio.getVolume", "version": "1.0"},
                {"name": "audio.setMute", "version": "1.0"},
                {"name": "system.info", "version": "2.0"},
            ]
        }

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features"])

        assert "AUDIO:" in result.output
        assert "SYSTEM:" in result.output

    def test_discover_features_shows_implemented_features(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features shows implemented CLI features."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {"services": []}

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features"])

        assert "IMPLEMENTED FEATURES" in result.output
        assert "Power Control" in result.output
        assert "Volume & Audio" in result.output
        assert "Applications" in result.output

    def test_discover_features_shows_limitations(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features shows known limitations."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {"services": []}

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features"])

        assert "KNOWN LIMITATIONS" in result.output
        assert "Screenshot capture" in result.output

    def test_discover_features_handles_no_services(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features handles when service list not available."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {}

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features"])

        assert result.exit_code == 0
        assert "Service list not available" in result.output

    def test_discover_features_handles_request_error(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features handles errors when querying services."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.side_effect = Exception("Request failed")

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features"])

        assert result.exit_code == 0
        assert "Could not retrieve service list" in result.output

    def test_discover_features_with_tv_option(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features accepts --tv option."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {"services": []}

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features", "--tv", "bedroom"])

        assert result.exit_code == 0

    def test_discover_features_with_ip_option(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features accepts --ip option."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {"services": []}

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features", "--ip", "192.168.1.200"])

        assert result.exit_code == 0

    def test_discover_features_connection_error(self, cli_runner, sample_config):
        """discover-features handles connection errors."""
        from lgtv.tv import TVConnectionError

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController", side_effect=TVConnectionError("Connection failed")):
            result = cli_runner.invoke(main, ["discover-features"])

        assert "Connection failed" in result.output

    def test_discover_features_auth_error(self, cli_runner, sample_config):
        """discover-features handles authentication errors."""
        from lgtv.tv import TVAuthenticationError

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController", side_effect=TVAuthenticationError("Auth failed")):
            result = cli_runner.invoke(main, ["discover-features"])

        assert "Auth failed" in result.output

    def test_discover_features_generic_error(self, cli_runner, sample_config):
        """discover-features handles generic errors."""
        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController", side_effect=Exception("Something went wrong")):
            result = cli_runner.invoke(main, ["discover-features"])

        assert "Failed to discover" in result.output

    def test_discover_features_service_without_dot(self, cli_runner, sample_config, mock_tv_controller_factory):
        """discover-features handles services without category prefix."""
        mock_controller = mock_tv_controller_factory()
        mock_controller.client = MagicMock()
        mock_controller.client.request.return_value = {
            "services": [
                {"name": "someService", "version": "1.0"},
            ]
        }

        with patch("lgtv.commands.discover_features.Config", return_value=sample_config), \
             patch("lgtv.commands.discover_features.TVController") as MockTV:
            MockTV.return_value.__enter__ = MagicMock(return_value=mock_controller)
            MockTV.return_value.__exit__ = MagicMock(return_value=False)

            result = cli_runner.invoke(main, ["discover-features"])

        assert result.exit_code == 0
        assert "OTHER:" in result.output
