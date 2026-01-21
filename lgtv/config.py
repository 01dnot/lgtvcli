"""Configuration management for LG TV CLI."""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class Config:
    """Manages configuration for LG TV connections."""

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to config file. Defaults to ~/.config/lgtv/config.json
        """
        if config_path:
            self.config_path = Path(config_path)
        else:
            config_dir = Path.home() / ".config" / "lgtv"
            self.config_path = config_dir / "config.json"

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self._data = self._load()

    def _load(self) -> Dict:
        """Load configuration from file."""
        if not self.config_path.exists():
            return {"default_tv": None, "tvs": {}}

        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {"default_tv": None, "tvs": {}}

    def save(self):
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def add_tv(self, name: str, ip: str, mac: Optional[str] = None,
               key: Optional[str] = None, model: Optional[str] = None):
        """Add or update a TV configuration.

        Args:
            name: Friendly name for the TV
            ip: IP address of the TV
            mac: MAC address for Wake-on-LAN (optional)
            key: Pairing key for authentication (optional)
            model: TV model information (optional)
        """
        self._data["tvs"][name] = {
            "name": name,
            "ip": ip,
            "mac": mac,
            "key": key,
            "model": model,
        }

        # Set as default if it's the first TV
        if self._data["default_tv"] is None:
            self._data["default_tv"] = name

        self.save()

    def remove_tv(self, name: str):
        """Remove a TV configuration.

        Args:
            name: Name of the TV to remove
        """
        if name in self._data["tvs"]:
            del self._data["tvs"][name]

            # Clear default if it was the removed TV
            if self._data["default_tv"] == name:
                # Set to another TV if available
                if self._data["tvs"]:
                    self._data["default_tv"] = next(iter(self._data["tvs"]))
                else:
                    self._data["default_tv"] = None

            self.save()

    def get_tv(self, name: Optional[str] = None) -> Optional[Dict]:
        """Get TV configuration by name or default.

        Args:
            name: Name of the TV, or None for default TV

        Returns:
            TV configuration dict or None if not found
        """
        if name is None:
            name = self._data["default_tv"]

        if name is None:
            return None

        return self._data["tvs"].get(name)

    def list_tvs(self) -> Dict[str, Dict]:
        """Get all configured TVs.

        Returns:
            Dictionary of TV configurations
        """
        return self._data["tvs"]

    def get_default_tv(self) -> Optional[str]:
        """Get the name of the default TV.

        Returns:
            Name of default TV or None
        """
        return self._data["default_tv"]

    def set_default_tv(self, name: str):
        """Set the default TV.

        Args:
            name: Name of the TV to set as default

        Raises:
            ValueError: If TV name doesn't exist
        """
        if name not in self._data["tvs"]:
            raise ValueError(f"TV '{name}' not found in configuration")

        self._data["default_tv"] = name
        self.save()

    def update_tv_key(self, name: str, key: str):
        """Update the pairing key for a TV.

        Args:
            name: Name of the TV
            key: New pairing key

        Raises:
            ValueError: If TV name doesn't exist
        """
        if name not in self._data["tvs"]:
            raise ValueError(f"TV '{name}' not found in configuration")

        self._data["tvs"][name]["key"] = key
        self.save()

    def update_tv_mac(self, name: str, mac: str):
        """Update the MAC address for a TV.

        Args:
            name: Name of the TV
            mac: New MAC address

        Raises:
            ValueError: If TV name doesn't exist
        """
        if name not in self._data["tvs"]:
            raise ValueError(f"TV '{name}' not found in configuration")

        self._data["tvs"][name]["mac"] = mac
        self.save()
