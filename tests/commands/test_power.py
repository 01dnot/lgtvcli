"""Tests for lgtv.commands.power module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.power import power
from lgtv.tv import TVConnectionError, TVAuthenticationError


@pytest.fixture
def runner():
    """Click CLI runner."""
    return CliRunner()


@pytest.fixture
def mock_config(sample_config):
    """Config fixture that patches the pass_config decorator."""
    return sample_config


class TestPowerOn:
    """Tests for power on command."""

    def test_power_on_success(self, runner, sample_config):
        """power on sends WoL packet and verifies TV response."""
        with patch("lgtv.commands.power.wake_on_lan") as mock_wol, \
             patch("lgtv.commands.power.TVController") as MockController:
            # Mock successful connection after WoL
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["on"], obj=sample_config)

            assert result.exit_code == 0
            mock_wol.assert_called_once()
            assert "Wake-on-LAN packet sent" in result.output

    def test_power_on_no_mac(self, runner, sample_config):
        """power on fails when MAC address not configured."""
        # Remove MAC from config
        sample_config._data["tvs"]["living_room"]["mac"] = None
        sample_config.save()

        result = runner.invoke(power, ["on"], obj=sample_config)

        assert result.exit_code != 0
        assert "MAC address not configured" in result.output

    def test_power_on_no_tv_configured(self, runner, empty_config):
        """power on fails when no TV is configured."""
        result = runner.invoke(power, ["on"], obj=empty_config)

        assert result.exit_code != 0
        assert "No TV configured" in result.output

    def test_power_on_with_ip_no_mac(self, runner, sample_config):
        """power on with --ip warns about missing MAC."""
        result = runner.invoke(power, ["on", "--ip", "192.168.1.200"], obj=sample_config)

        assert "Warning" in result.output
        assert "MAC address needed" in result.output


class TestPowerOff:
    """Tests for power off command."""

    def test_power_off_success(self, runner, sample_config):
        """power off sends power_off command."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["off"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.system.power_off.assert_called_once()
            assert "TV powered off" in result.output

    def test_power_off_connection_error(self, runner, sample_config):
        """power off handles connection errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVConnectionError("TV unreachable")

            result = runner.invoke(power, ["off"], obj=sample_config)

            assert result.exit_code != 0
            assert "TV unreachable" in result.output

    def test_power_off_auth_error(self, runner, sample_config):
        """power off handles authentication errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(power, ["off"], obj=sample_config)

            assert result.exit_code != 0
            assert "Auth failed" in result.output

    def test_power_off_with_tv_option(self, runner, sample_config):
        """power off accepts --tv option."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["off", "--tv", "bedroom"], obj=sample_config)

            assert result.exit_code == 0
            MockController.assert_called_with(sample_config, tv_name="bedroom", ip=None)


class TestScreenOff:
    """Tests for screen-off command."""

    def test_screen_off_success(self, runner, sample_config):
        """screen-off sends screen_off command."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["screen-off"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.system.screen_off.assert_called_once()
            assert "Screen turned off" in result.output

    def test_screen_off_connection_error(self, runner, sample_config):
        """screen-off handles connection errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(power, ["screen-off"], obj=sample_config)

            assert result.exit_code != 0


class TestScreenOn:
    """Tests for screen-on command."""

    def test_screen_on_success(self, runner, sample_config):
        """screen-on sends screen_on command."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["screen-on"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.system.screen_on.assert_called_once()
            assert "Screen turned on" in result.output


class TestPowerStatus:
    """Tests for power status command."""

    def test_power_status_tv_on(self, runner, sample_config):
        """power status reports TV is on when responsive."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.return_value = {
                "modelName": "OLED65C1",
                "sdkVersion": "7.0.0",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "TV is ON" in result.output
            assert "OLED65C1" in result.output

    def test_power_status_tv_off(self, runner, sample_config):
        """power status reports TV is off when connection fails."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Unreachable")

            result = runner.invoke(power, ["status"], obj=sample_config)

            assert result.exit_code == 0
            assert "TV is OFF" in result.output

    def test_power_status_auth_error(self, runner, sample_config):
        """power status handles auth errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(power, ["status"], obj=sample_config)

            assert result.exit_code != 0
            assert "Auth failed" in result.output

    def test_power_status_generic_error(self, runner, sample_config):
        """power status handles generic errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["status"], obj=sample_config)

            assert "Failed to get power status" in result.output


class TestPowerOnEdgeCases:
    """Tests for power on edge cases."""

    def test_power_on_wol_sent_tv_not_responding(self, runner, sample_config):
        """power on warns when TV doesn't respond after WoL."""
        with patch("lgtv.commands.power.wake_on_lan") as mock_wol, \
             patch("lgtv.commands.power.TVController") as MockController, \
             patch("lgtv.commands.power.time.sleep"):
            # Mock connection failure after WoL
            MockController.side_effect = TVConnectionError("Not responding")

            result = runner.invoke(power, ["on"], obj=sample_config)

            # Should still exit ok, just with warning
            mock_wol.assert_called_once()
            assert "did not respond" in result.output or "still be starting" in result.output

    def test_power_on_generic_error(self, runner, sample_config):
        """power on handles generic errors."""
        with patch("lgtv.commands.power.wake_on_lan", side_effect=Exception("Network error")):
            result = runner.invoke(power, ["on"], obj=sample_config)

            assert "Network error" in result.output


class TestPowerOffEdgeCases:
    """Tests for power off edge cases."""

    def test_power_off_generic_error(self, runner, sample_config):
        """power off handles generic errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.power_off.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["off"], obj=sample_config)

            assert "Failed to power off" in result.output


class TestScreenOffEdgeCases:
    """Tests for screen-off edge cases."""

    def test_screen_off_auth_error(self, runner, sample_config):
        """screen-off handles auth errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(power, ["screen-off"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_screen_off_generic_error(self, runner, sample_config):
        """screen-off handles generic errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.screen_off.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["screen-off"], obj=sample_config)

            assert "Failed to turn screen off" in result.output


class TestScreenOnEdgeCases:
    """Tests for screen-on edge cases."""

    def test_screen_on_connection_error(self, runner, sample_config):
        """screen-on handles connection errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(power, ["screen-on"], obj=sample_config)

            assert "Connection failed" in result.output

    def test_screen_on_auth_error(self, runner, sample_config):
        """screen-on handles auth errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            MockController.side_effect = TVAuthenticationError("Auth failed")

            result = runner.invoke(power, ["screen-on"], obj=sample_config)

            assert "Auth failed" in result.output

    def test_screen_on_generic_error(self, runner, sample_config):
        """screen-on handles generic errors."""
        with patch("lgtv.commands.power.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.screen_on.side_effect = Exception("Boom")
            MockController.return_value = mock_controller

            result = runner.invoke(power, ["screen-on"], obj=sample_config)

            assert "Failed to turn screen on" in result.output
