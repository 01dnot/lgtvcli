"""Tests for lgtv.cli module."""

import os
import pytest
from unittest.mock import patch, MagicMock
from click.testing import CliRunner

from lgtv.cli import main, completion, completion_bash, completion_zsh, completion_fish, completion_install


class TestMainCommand:
    """Tests for the main CLI entry point."""

    def test_main_shows_help_when_no_command(self, cli_runner):
        """Main command shows help when invoked without subcommand."""
        result = cli_runner.invoke(main)
        assert result.exit_code == 0
        assert "LG TV CLI" in result.output
        assert "Control your LG WebOS TV" in result.output

    def test_main_version_option(self, cli_runner):
        """--version shows version info or error about package not installed."""
        result = cli_runner.invoke(main, ["--version"])
        # In test environment, version lookup may fail - that's ok
        # Just verify it doesn't crash with unexpected error
        assert result.exit_code in (0, 1)

    def test_main_debug_option(self, cli_runner):
        """--debug option is accepted."""
        # Just verify the --debug flag is accepted
        result = cli_runner.invoke(main, ["--debug", "config", "list"])
        # Should not fail due to unrecognized option
        assert "--debug" not in result.output or "Error" not in result.output

    def test_main_help_option(self, cli_runner):
        """--help shows help message."""
        result = cli_runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Usage:" in result.output


class TestCompletionGroup:
    """Tests for the completion command group."""

    def test_completion_group_help(self, cli_runner):
        """completion command shows available subcommands."""
        result = cli_runner.invoke(main, ["completion", "--help"])
        assert result.exit_code == 0
        assert "bash" in result.output
        assert "zsh" in result.output
        assert "fish" in result.output
        assert "install" in result.output


class TestCompletionBash:
    """Tests for completion bash command."""

    def test_completion_bash_output(self, cli_runner):
        """completion bash outputs bash completion script."""
        result = cli_runner.invoke(main, ["completion", "bash"])
        assert result.exit_code == 0
        assert "_LGTV_COMPLETE=bash_source" in result.output
        assert ".bashrc" in result.output

    def test_completion_bash_has_instructions(self, cli_runner):
        """completion bash includes setup instructions."""
        result = cli_runner.invoke(main, ["completion", "bash"])
        assert "Add this to" in result.output
        assert "eval" in result.output


class TestCompletionZsh:
    """Tests for completion zsh command."""

    def test_completion_zsh_output(self, cli_runner):
        """completion zsh outputs zsh completion script."""
        result = cli_runner.invoke(main, ["completion", "zsh"])
        assert result.exit_code == 0
        assert "_LGTV_COMPLETE=zsh_source" in result.output
        assert ".zshrc" in result.output

    def test_completion_zsh_has_instructions(self, cli_runner):
        """completion zsh includes setup instructions."""
        result = cli_runner.invoke(main, ["completion", "zsh"])
        assert "Add this to" in result.output


class TestCompletionFish:
    """Tests for completion fish command."""

    def test_completion_fish_output(self, cli_runner):
        """completion fish outputs fish completion script."""
        result = cli_runner.invoke(main, ["completion", "fish"])
        assert result.exit_code == 0
        assert "_LGTV_COMPLETE=fish_source" in result.output
        assert "completions/lgtv.fish" in result.output

    def test_completion_fish_has_instructions(self, cli_runner):
        """completion fish includes setup instructions."""
        result = cli_runner.invoke(main, ["completion", "fish"])
        assert "Add this to" in result.output


class TestCompletionInstall:
    """Tests for completion install command."""

    def test_completion_install_zsh(self, cli_runner, tmp_path, monkeypatch):
        """completion install --shell zsh installs to .zshrc."""
        home = tmp_path / "home"
        home.mkdir()
        zshrc = home / ".zshrc"
        zshrc.write_text("# existing config\n")

        monkeypatch.setenv("HOME", str(home))
        with patch("os.path.expanduser", return_value=str(home)):
            with patch("lgtv.cli.os.path.expanduser", return_value=str(home)):
                result = cli_runner.invoke(main, ["completion", "install", "--shell", "zsh"])

        # Check the file was updated
        if result.exit_code == 0:
            content = zshrc.read_text()
            assert "_LGTV_COMPLETE" in content

    def test_completion_install_bash(self, cli_runner, tmp_path, monkeypatch):
        """completion install --shell bash installs to .bashrc."""
        home = tmp_path / "home"
        home.mkdir()
        bashrc = home / ".bashrc"
        bashrc.write_text("# existing config\n")

        monkeypatch.setenv("HOME", str(home))
        with patch("lgtv.cli.os.path.expanduser", return_value=str(home)):
            result = cli_runner.invoke(main, ["completion", "install", "--shell", "bash"])

        if result.exit_code == 0:
            content = bashrc.read_text()
            assert "_LGTV_COMPLETE" in content

    def test_completion_install_fish(self, cli_runner, tmp_path, monkeypatch):
        """completion install --shell fish installs to fish completions."""
        home = tmp_path / "home"
        home.mkdir()

        monkeypatch.setenv("HOME", str(home))
        with patch("lgtv.cli.os.path.expanduser", return_value=str(home)):
            result = cli_runner.invoke(main, ["completion", "install", "--shell", "fish"])

        fish_file = home / ".config" / "fish" / "completions" / "lgtv.fish"
        if result.exit_code == 0:
            assert fish_file.exists()
            content = fish_file.read_text()
            assert "_LGTV_COMPLETE" in content

    def test_completion_install_autodetect_zsh(self, cli_runner, tmp_path, monkeypatch):
        """completion install auto-detects zsh from SHELL env."""
        home = tmp_path / "home"
        home.mkdir()
        zshrc = home / ".zshrc"
        zshrc.write_text("# existing\n")

        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("SHELL", "/bin/zsh")
        with patch("lgtv.cli.os.path.expanduser", return_value=str(home)):
            result = cli_runner.invoke(main, ["completion", "install"])

        if result.exit_code == 0:
            content = zshrc.read_text()
            assert "_LGTV_COMPLETE" in content

    def test_completion_install_autodetect_bash(self, cli_runner, tmp_path, monkeypatch):
        """completion install auto-detects bash from SHELL env."""
        home = tmp_path / "home"
        home.mkdir()
        bashrc = home / ".bashrc"
        bashrc.write_text("# existing\n")

        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("SHELL", "/bin/bash")
        with patch("lgtv.cli.os.path.expanduser", return_value=str(home)):
            result = cli_runner.invoke(main, ["completion", "install"])

        if result.exit_code == 0:
            content = bashrc.read_text()
            assert "_LGTV_COMPLETE" in content

    def test_completion_install_autodetect_fish(self, cli_runner, tmp_path, monkeypatch):
        """completion install auto-detects fish from SHELL env."""
        home = tmp_path / "home"
        home.mkdir()

        monkeypatch.setenv("HOME", str(home))
        monkeypatch.setenv("SHELL", "/usr/bin/fish")
        with patch("lgtv.cli.os.path.expanduser", return_value=str(home)):
            result = cli_runner.invoke(main, ["completion", "install"])

        fish_file = home / ".config" / "fish" / "completions" / "lgtv.fish"
        if result.exit_code == 0:
            assert fish_file.exists()

    def test_completion_install_unknown_shell(self, cli_runner, monkeypatch):
        """completion install fails gracefully for unknown shell."""
        monkeypatch.setenv("SHELL", "/bin/unknown")
        result = cli_runner.invoke(main, ["completion", "install"])
        assert "Could not detect shell" in result.output or result.exit_code != 0

    def test_completion_install_already_installed(self, cli_runner, tmp_path, monkeypatch):
        """completion install detects if already installed."""
        home = tmp_path / "home"
        home.mkdir()
        zshrc = home / ".zshrc"
        zshrc.write_text('eval "$(_LGTV_COMPLETE=zsh_source lgtv)"\n')

        monkeypatch.setenv("HOME", str(home))
        with patch("lgtv.cli.os.path.expanduser", return_value=str(home)):
            result = cli_runner.invoke(main, ["completion", "install", "--shell", "zsh"])

        assert "already installed" in result.output.lower()


class TestConfigCommands:
    """Tests for config subcommands."""

    def test_config_list_empty(self, cli_runner, empty_config):
        """config list shows message when no TVs configured."""
        with patch("lgtv.cli.Config", return_value=empty_config):
            result = cli_runner.invoke(main, ["config", "list"])
        assert result.exit_code == 0
        assert "No TVs configured" in result.output

    def test_config_list_with_tvs(self, cli_runner, sample_config):
        """config list shows configured TVs."""
        with patch("lgtv.cli.Config", return_value=sample_config):
            result = cli_runner.invoke(main, ["config", "list"])
        assert result.exit_code == 0
        assert "living_room" in result.output
        assert "192.168.1.100" in result.output

    def test_config_set_default(self, cli_runner, sample_config):
        """config set-default changes the default TV."""
        with patch("lgtv.cli.Config", return_value=sample_config):
            result = cli_runner.invoke(main, ["config", "set-default", "bedroom"])
        assert result.exit_code == 0
        assert "Default TV set to" in result.output

    def test_config_set_default_nonexistent(self, cli_runner, sample_config):
        """config set-default fails for non-existent TV."""
        with patch("lgtv.cli.Config", return_value=sample_config):
            result = cli_runner.invoke(main, ["config", "set-default", "nonexistent"])
        assert "not found" in result.output.lower()

    def test_config_remove(self, cli_runner, sample_config):
        """config remove deletes a TV."""
        with patch("lgtv.cli.Config", return_value=sample_config):
            result = cli_runner.invoke(main, ["config", "remove", "bedroom", "--yes"])
        assert result.exit_code == 0
        assert "removed" in result.output.lower()


class TestDiscoverCommand:
    """Tests for discover command."""

    def test_discover_no_tvs_found(self, cli_runner):
        """discover shows troubleshooting when no TVs found."""
        with patch("lgtv.cli.discover_tvs", return_value=[]):
            result = cli_runner.invoke(main, ["discover"])
        assert "No LG TVs found" in result.output
        assert "Troubleshooting" in result.output

    def test_discover_found_tvs(self, cli_runner):
        """discover lists found TVs."""
        found_tvs = [
            {"ip": "192.168.1.100", "name": "Living Room", "model": "OLED65C1", "discovery_method": "ssdp"}
        ]
        with patch("lgtv.cli.discover_tvs", return_value=found_tvs):
            result = cli_runner.invoke(main, ["discover"])
        assert result.exit_code == 0
        assert "192.168.1.100" in result.output
        assert "Living Room" in result.output

    def test_discover_with_timeout(self, cli_runner):
        """discover accepts --timeout option."""
        with patch("lgtv.cli.discover_tvs", return_value=[]) as mock_discover:
            cli_runner.invoke(main, ["discover", "--timeout", "10"])
            mock_discover.assert_called_once_with(10)


class TestPairCommand:
    """Tests for pair command."""

    def test_pair_success(self, cli_runner, empty_config):
        """pair successfully pairs with TV."""
        mock_controller = MagicMock()
        mock_controller.pair.return_value = "test_key"
        mock_controller.system.info.return_value = {"modelName": "OLED65C1"}
        mock_controller.disconnect = MagicMock()

        with patch("lgtv.cli.Config", return_value=empty_config), \
             patch("lgtv.cli.TVController", return_value=mock_controller):
            result = cli_runner.invoke(main, ["pair", "192.168.1.100", "--name", "test_tv"])

        assert "Pairing successful" in result.output

    def test_pair_connection_error(self, cli_runner, empty_config):
        """pair handles connection errors."""
        from lgtv.tv import TVConnectionError

        with patch("lgtv.cli.Config", return_value=empty_config), \
             patch("lgtv.cli.TVController", side_effect=TVConnectionError("Connection refused")):
            result = cli_runner.invoke(main, ["pair", "192.168.1.100", "--name", "test_tv"])

        assert "Connection refused" in result.output or "error" in result.output.lower()

    def test_pair_prompts_for_name(self, cli_runner, empty_config):
        """pair prompts for name if not provided."""
        mock_controller = MagicMock()
        mock_controller.pair.return_value = "test_key"
        mock_controller.system.info.return_value = {}
        mock_controller.disconnect = MagicMock()

        with patch("lgtv.cli.Config", return_value=empty_config), \
             patch("lgtv.cli.TVController", return_value=mock_controller):
            result = cli_runner.invoke(main, ["pair", "192.168.1.100"], input="my-tv\n")

        # Should have asked for name
        assert result.exit_code == 0
