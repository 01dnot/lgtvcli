"""Tests for lgtv.commands.control module."""

import pytest
from unittest.mock import MagicMock, patch
from click.testing import CliRunner

from lgtv.commands.control import button, notify, keyboard, mouse, inspect, VALID_BUTTONS
from lgtv.tv import TVConnectionError, TVAuthenticationError


@pytest.fixture
def runner():
    """Click CLI runner."""
    return CliRunner()


class TestButton:
    """Tests for button command."""

    @pytest.mark.parametrize("btn", ["home", "back", "up", "down", "left", "right", "ok"])
    def test_button_navigation(self, runner, sample_config, btn):
        """button sends navigation button commands."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(button, [btn], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.connect_input.assert_called_once()
            assert "Button pressed" in result.output
            assert btn in result.output

    def test_button_home(self, runner, sample_config):
        """button home calls input.home()."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(button, ["home"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.home.assert_called_once()

    def test_button_back(self, runner, sample_config):
        """button back calls input.back()."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(button, ["back"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.back.assert_called_once()

    @pytest.mark.parametrize("btn", ["menu", "info", "exit", "dash"])
    def test_button_menu_buttons(self, runner, sample_config, btn):
        """button sends menu button commands."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(button, [btn], obj=sample_config)

            assert result.exit_code == 0
            getattr(mock_controller.input, btn).assert_called_once()

    @pytest.mark.parametrize("btn", ["red", "green", "yellow", "blue"])
    def test_button_color_buttons(self, runner, sample_config, btn):
        """button sends color button commands."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(button, [btn], obj=sample_config)

            assert result.exit_code == 0
            getattr(mock_controller.input, btn).assert_called_once()

    @pytest.mark.parametrize("btn", ["0", "1", "5", "9"])
    def test_button_number_buttons(self, runner, sample_config, btn):
        """button sends number button commands."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(button, [btn], obj=sample_config)

            assert result.exit_code == 0
            getattr(mock_controller.input, f"num_{btn}").assert_called_once()

    def test_button_enter_maps_to_ok(self, runner, sample_config):
        """button enter calls input.ok()."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(button, ["enter"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.ok.assert_called_once()

    def test_button_invalid(self, runner, sample_config):
        """button rejects invalid button names."""
        result = runner.invoke(button, ["invalid_button"], obj=sample_config)

        assert result.exit_code != 0

    def test_button_connection_error(self, runner, sample_config):
        """button handles connection errors."""
        with patch("lgtv.commands.control.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(button, ["home"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output


class TestNotify:
    """Tests for notify command."""

    def test_notify_success(self, runner, sample_config):
        """notify sends notification to TV."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(notify, ["Hello, TV!"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.system.notify.assert_called_once_with("Hello, TV!")
            assert "Notification sent" in result.output

    def test_notify_connection_error(self, runner, sample_config):
        """notify handles connection errors."""
        with patch("lgtv.commands.control.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(notify, ["Hello"], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output


class TestKeyboard:
    """Tests for keyboard command."""

    def test_keyboard_success(self, runner, sample_config):
        """keyboard sends text to TV."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(keyboard, ["search text"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.connect_input.assert_called_once()
            mock_controller.input.type.assert_called_once_with("search text")
            assert "Typed" in result.output

    def test_keyboard_connection_error(self, runner, sample_config):
        """keyboard handles connection errors."""
        with patch("lgtv.commands.control.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(keyboard, ["text"], obj=sample_config)

            assert result.exit_code != 0


class TestMouseMove:
    """Tests for mouse move command."""

    def test_mouse_move_success(self, runner, sample_config):
        """mouse move sends cursor movement."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(mouse, ["move", "10", "5"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.connect_input.assert_called_once()
            mock_controller.input.move.assert_called_once_with(10, 5)
            assert "Moved cursor" in result.output

    def test_mouse_move_negative_values(self, runner, sample_config):
        """mouse move accepts negative values."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            # Use -- to separate options from arguments, allowing negative values
            result = runner.invoke(mouse, ["move", "--", "-50", "-100"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.move.assert_called_once_with(-50, -100)


class TestMouseClick:
    """Tests for mouse click command."""

    def test_mouse_click_success(self, runner, sample_config):
        """mouse click sends click event."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            MockController.return_value = mock_controller

            result = runner.invoke(mouse, ["click"], obj=sample_config)

            assert result.exit_code == 0
            mock_controller.input.connect_input.assert_called_once()
            mock_controller.input.click.assert_called_once()
            assert "clicked" in result.output


class TestInspect:
    """Tests for inspect command."""

    def test_inspect_success(self, runner, sample_config):
        """inspect shows detailed TV state."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.return_value = {
                "modelName": "OLED65C1",
                "sdkVersion": "7.0.0",
            }
            mock_controller.app.get_current.return_value = {
                "appId": "netflix",
                "title": "Netflix",
            }
            mock_controller.tv.get_current_channel.return_value = None
            mock_controller.media.get_volume.return_value = {
                "volume": 25,
                "muted": False,
            }
            mock_controller.media.get_audio_output.return_value = {
                "soundOutput": "tv_speaker",
            }
            MockController.return_value = mock_controller

            result = runner.invoke(inspect, [], obj=sample_config)

            assert result.exit_code == 0
            assert "System" in result.output
            assert "Application" in result.output
            assert "Audio" in result.output
            assert "OLED65C1" in result.output
            assert "Netflix" in result.output

    def test_inspect_connection_error(self, runner, sample_config):
        """inspect handles connection errors."""
        with patch("lgtv.commands.control.TVController") as MockController:
            MockController.side_effect = TVConnectionError("Connection failed")

            result = runner.invoke(inspect, [], obj=sample_config)

            assert result.exit_code != 0
            assert "Connection failed" in result.output

    def test_inspect_partial_info(self, runner, sample_config):
        """inspect handles partial information gracefully."""
        with patch("lgtv.commands.control.TVController") as MockController:
            mock_controller = MagicMock()
            mock_controller.__enter__ = MagicMock(return_value=mock_controller)
            mock_controller.__exit__ = MagicMock(return_value=False)
            mock_controller.system.info.side_effect = Exception("Info not available")
            mock_controller.app.get_current.return_value = {"appId": "youtube"}
            mock_controller.tv.get_current_channel.side_effect = Exception()
            mock_controller.media.get_volume.side_effect = Exception()
            mock_controller.media.get_audio_output.side_effect = Exception()
            MockController.return_value = mock_controller

            result = runner.invoke(inspect, [], obj=sample_config)

            assert result.exit_code == 0
            assert "Unable to retrieve" in result.output
            assert "youtube" in result.output


class TestValidButtons:
    """Tests for VALID_BUTTONS constant."""

    def test_valid_buttons_contains_essentials(self):
        """VALID_BUTTONS contains essential buttons."""
        assert "home" in VALID_BUTTONS
        assert "back" in VALID_BUTTONS
        assert "ok" in VALID_BUTTONS
        assert "up" in VALID_BUTTONS
        assert "down" in VALID_BUTTONS
        assert "left" in VALID_BUTTONS
        assert "right" in VALID_BUTTONS

    def test_valid_buttons_contains_numbers(self):
        """VALID_BUTTONS contains number buttons."""
        for i in range(10):
            assert str(i) in VALID_BUTTONS

    def test_valid_buttons_contains_colors(self):
        """VALID_BUTTONS contains color buttons."""
        assert "red" in VALID_BUTTONS
        assert "green" in VALID_BUTTONS
        assert "yellow" in VALID_BUTTONS
        assert "blue" in VALID_BUTTONS
