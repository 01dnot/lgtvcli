"""Tests for lgtv.config module."""

import json
import pytest
from pathlib import Path

from lgtv.config import Config


class TestConfigInit:
    """Tests for Config initialization."""

    def test_init_creates_default_directory(self, tmp_path, monkeypatch):
        """Config creates ~/.config/lgtv directory if it doesn't exist."""
        fake_home = tmp_path / "home"
        fake_home.mkdir()
        monkeypatch.setenv("HOME", str(fake_home))

        # Patch Path.home() to return our fake home
        monkeypatch.setattr(Path, "home", lambda: fake_home)

        config = Config()

        assert (fake_home / ".config" / "lgtv").exists()
        assert config.config_path == fake_home / ".config" / "lgtv" / "config.json"

    def test_init_with_custom_path(self, temp_config_path):
        """Config accepts custom config_path."""
        config = Config(config_path=temp_config_path)
        assert str(config.config_path) == temp_config_path

    def test_init_creates_parent_directories(self, tmp_path):
        """Config creates parent directories for custom path."""
        nested_path = tmp_path / "deep" / "nested" / "config.json"
        Config(config_path=str(nested_path))  # noqa: F841
        assert nested_path.parent.exists()

    def test_init_with_empty_config_file(self, temp_config_path):
        """Config initializes with empty data when file doesn't exist."""
        config = Config(config_path=temp_config_path)
        assert config._data == {"default_tv": None, "tvs": {}}

    def test_init_loads_existing_config(self, temp_config_path):
        """Config loads existing configuration from file."""
        existing_data = {
            "default_tv": "test_tv",
            "tvs": {
                "test_tv": {
                    "name": "test_tv",
                    "ip": "1.2.3.4",
                    "mac": None,
                    "key": None,
                    "model": None,
                }
            }
        }
        with open(temp_config_path, "w") as f:
            json.dump(existing_data, f)

        config = Config(config_path=temp_config_path)
        assert config._data == existing_data

    def test_init_handles_corrupted_json(self, temp_config_path):
        """Config handles corrupted JSON gracefully."""
        with open(temp_config_path, "w") as f:
            f.write("not valid json {{{")

        config = Config(config_path=temp_config_path)
        assert config._data == {"default_tv": None, "tvs": {}}


class TestAddTv:
    """Tests for Config.add_tv method."""

    def test_add_tv_basic(self, empty_config):
        """add_tv adds a TV with minimal required fields."""
        empty_config.add_tv("test_tv", "192.168.1.100")

        tv = empty_config.get_tv("test_tv")
        assert tv["name"] == "test_tv"
        assert tv["ip"] == "192.168.1.100"
        assert tv["mac"] is None
        assert tv["key"] is None
        assert tv["model"] is None

    def test_add_tv_with_all_fields(self, empty_config):
        """add_tv accepts all optional fields."""
        empty_config.add_tv(
            name="test_tv",
            ip="192.168.1.100",
            mac="AA:BB:CC:DD:EE:FF",
            key="test_key_123",
            model="OLED65C1",
        )

        tv = empty_config.get_tv("test_tv")
        assert tv["name"] == "test_tv"
        assert tv["ip"] == "192.168.1.100"
        assert tv["mac"] == "AA:BB:CC:DD:EE:FF"
        assert tv["key"] == "test_key_123"
        assert tv["model"] == "OLED65C1"

    def test_add_tv_sets_default_if_first(self, empty_config):
        """First TV added becomes the default."""
        empty_config.add_tv("first_tv", "192.168.1.100")
        assert empty_config.get_default_tv() == "first_tv"

    def test_add_tv_preserves_existing_default(self, sample_config):
        """Adding a second TV doesn't change the default."""
        original_default = sample_config.get_default_tv()
        sample_config.add_tv("new_tv", "192.168.1.200")
        assert sample_config.get_default_tv() == original_default

    def test_add_tv_updates_existing(self, sample_config):
        """add_tv updates an existing TV with the same name."""
        sample_config.add_tv("living_room", "192.168.1.999", mac="NEW:MAC:ADDR")

        tv = sample_config.get_tv("living_room")
        assert tv["ip"] == "192.168.1.999"
        assert tv["mac"] == "NEW:MAC:ADDR"

    def test_add_tv_persists_to_file(self, temp_config_path):
        """add_tv saves changes to the config file."""
        config = Config(config_path=temp_config_path)
        config.add_tv("test_tv", "192.168.1.100")

        # Reload from file
        new_config = Config(config_path=temp_config_path)
        assert new_config.get_tv("test_tv") is not None


class TestRemoveTv:
    """Tests for Config.remove_tv method."""

    def test_remove_tv_basic(self, sample_config):
        """remove_tv removes an existing TV."""
        sample_config.remove_tv("bedroom")
        assert sample_config.get_tv("bedroom") is None

    def test_remove_tv_nonexistent(self, sample_config):
        """remove_tv handles non-existent TV gracefully."""
        # Should not raise
        sample_config.remove_tv("nonexistent")

    def test_remove_tv_updates_default(self, sample_config):
        """Removing the default TV sets another TV as default."""
        sample_config.remove_tv("living_room")
        # Should have set bedroom as new default
        assert sample_config.get_default_tv() == "bedroom"

    def test_remove_tv_clears_default_when_last(self, empty_config):
        """Removing the last TV clears the default."""
        empty_config.add_tv("only_tv", "192.168.1.100")
        empty_config.remove_tv("only_tv")
        assert empty_config.get_default_tv() is None

    def test_remove_tv_persists_to_file(self, sample_config, temp_config_path):
        """remove_tv saves changes to the config file."""
        sample_config.remove_tv("bedroom")

        # Get the actual config path from the sample_config
        config_path = str(sample_config.config_path)
        new_config = Config(config_path=config_path)
        assert new_config.get_tv("bedroom") is None


class TestGetTv:
    """Tests for Config.get_tv method."""

    def test_get_tv_by_name(self, sample_config):
        """get_tv returns TV config by name."""
        tv = sample_config.get_tv("living_room")
        assert tv["name"] == "living_room"
        assert tv["ip"] == "192.168.1.100"

    def test_get_tv_default(self, sample_config):
        """get_tv returns default TV when name is None."""
        tv = sample_config.get_tv(None)
        assert tv["name"] == "living_room"

    def test_get_tv_nonexistent(self, sample_config):
        """get_tv returns None for non-existent TV."""
        tv = sample_config.get_tv("nonexistent")
        assert tv is None

    def test_get_tv_no_default(self, empty_config):
        """get_tv returns None when no default is set."""
        tv = empty_config.get_tv(None)
        assert tv is None


class TestListTvs:
    """Tests for Config.list_tvs method."""

    def test_list_tvs_empty(self, empty_config):
        """list_tvs returns empty dict when no TVs configured."""
        assert empty_config.list_tvs() == {}

    def test_list_tvs_populated(self, sample_config):
        """list_tvs returns all configured TVs."""
        tvs = sample_config.list_tvs()
        assert "living_room" in tvs
        assert "bedroom" in tvs
        assert len(tvs) == 2


class TestDefaultTv:
    """Tests for default TV management."""

    def test_get_default_tv(self, sample_config):
        """get_default_tv returns the default TV name."""
        assert sample_config.get_default_tv() == "living_room"

    def test_get_default_tv_none(self, empty_config):
        """get_default_tv returns None when no default set."""
        assert empty_config.get_default_tv() is None

    def test_set_default_tv(self, sample_config):
        """set_default_tv changes the default TV."""
        sample_config.set_default_tv("bedroom")
        assert sample_config.get_default_tv() == "bedroom"

    def test_set_default_tv_nonexistent(self, sample_config):
        """set_default_tv raises ValueError for non-existent TV."""
        with pytest.raises(ValueError, match="TV 'nonexistent' not found"):
            sample_config.set_default_tv("nonexistent")

    def test_set_default_tv_persists(self, sample_config):
        """set_default_tv saves changes to the config file."""
        config_path = str(sample_config.config_path)
        sample_config.set_default_tv("bedroom")

        new_config = Config(config_path=config_path)
        assert new_config.get_default_tv() == "bedroom"


class TestUpdateTvKey:
    """Tests for Config.update_tv_key method."""

    def test_update_tv_key(self, sample_config):
        """update_tv_key updates the pairing key."""
        sample_config.update_tv_key("living_room", "new_key_456")
        tv = sample_config.get_tv("living_room")
        assert tv["key"] == "new_key_456"

    def test_update_tv_key_nonexistent(self, sample_config):
        """update_tv_key raises ValueError for non-existent TV."""
        with pytest.raises(ValueError, match="TV 'nonexistent' not found"):
            sample_config.update_tv_key("nonexistent", "key")

    def test_update_tv_key_persists(self, sample_config):
        """update_tv_key saves changes to the config file."""
        config_path = str(sample_config.config_path)
        sample_config.update_tv_key("living_room", "new_key_456")

        new_config = Config(config_path=config_path)
        tv = new_config.get_tv("living_room")
        assert tv["key"] == "new_key_456"


class TestUpdateTvMac:
    """Tests for Config.update_tv_mac method."""

    def test_update_tv_mac(self, sample_config):
        """update_tv_mac updates the MAC address."""
        sample_config.update_tv_mac("living_room", "FF:EE:DD:CC:BB:AA")
        tv = sample_config.get_tv("living_room")
        assert tv["mac"] == "FF:EE:DD:CC:BB:AA"

    def test_update_tv_mac_nonexistent(self, sample_config):
        """update_tv_mac raises ValueError for non-existent TV."""
        with pytest.raises(ValueError, match="TV 'nonexistent' not found"):
            sample_config.update_tv_mac("nonexistent", "mac")

    def test_update_tv_mac_persists(self, sample_config):
        """update_tv_mac saves changes to the config file."""
        config_path = str(sample_config.config_path)
        sample_config.update_tv_mac("living_room", "FF:EE:DD:CC:BB:AA")

        new_config = Config(config_path=config_path)
        tv = new_config.get_tv("living_room")
        assert tv["mac"] == "FF:EE:DD:CC:BB:AA"


class TestSave:
    """Tests for Config.save method."""

    def test_save_creates_file(self, temp_config_path):
        """save creates the config file if it doesn't exist."""
        config = Config(config_path=temp_config_path)
        config.add_tv("test", "1.2.3.4")

        assert Path(temp_config_path).exists()

    def test_save_writes_valid_json(self, temp_config_path):
        """save writes valid JSON to the config file."""
        config = Config(config_path=temp_config_path)
        config.add_tv("test", "1.2.3.4")

        with open(temp_config_path, "r") as f:
            data = json.load(f)

        assert "default_tv" in data
        assert "tvs" in data
        assert "test" in data["tvs"]

    def test_save_uses_indentation(self, temp_config_path):
        """save formats JSON with indentation for readability."""
        config = Config(config_path=temp_config_path)
        config.add_tv("test", "1.2.3.4")

        with open(temp_config_path, "r") as f:
            content = f.read()

        # Indented JSON should have newlines
        assert "\n" in content
