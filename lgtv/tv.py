"""TV connection wrapper for PyWebOSTV."""

import time
from typing import Optional, Dict, Any
from pywebostv.discovery import discover
from pywebostv.connection import WebOSClient
from pywebostv.controls import (
    SystemControl,
    MediaControl,
    ApplicationControl,
    InputControl,
    TvControl,
    SourceControl,
)

from .config import Config


class TVConnectionError(Exception):
    """Exception raised for TV connection errors."""
    pass


class TVAuthenticationError(Exception):
    """Exception raised for TV authentication errors."""
    pass


class TVController:
    """Wrapper for PyWebOSTV with configuration support."""

    def __init__(self, config: Config, tv_name: Optional[str] = None,
                 ip: Optional[str] = None, timeout: int = 10):
        """Initialize TV controller.

        Args:
            config: Configuration manager
            tv_name: Name of TV from config (optional)
            ip: Direct IP address (overrides config, optional)
            timeout: Connection timeout in seconds

        Raises:
            TVConnectionError: If connection fails
            TVAuthenticationError: If authentication fails
        """
        self.config = config
        self.timeout = timeout
        self.client = None
        self._system = None
        self._media = None
        self._app = None
        self._input = None
        self._tv = None
        self._source = None

        # Determine which TV to connect to
        if ip:
            self.ip = ip
            self.tv_name = None
            self.stored_key = None
        else:
            tv_config = config.get_tv(tv_name)
            if not tv_config:
                if tv_name:
                    raise TVConnectionError(f"TV '{tv_name}' not found in configuration")
                else:
                    raise TVConnectionError(
                        "No default TV configured. Use 'lgtv pair <ip>' to add a TV."
                    )

            self.ip = tv_config["ip"]
            self.tv_name = tv_config["name"]
            self.stored_key = tv_config.get("key")

        self._connect()

    def _connect(self):
        """Establish connection to the TV."""
        store = {"client_key": self.stored_key} if self.stored_key else {}

        # Try secure connection first (newer TVs), then fall back to non-secure
        last_error = None
        for secure in [True, False]:
            try:
                self.client = WebOSClient(self.ip, secure=secure)
                self.client.connect()

                # If we have a stored key, try to use it
                if self.stored_key:
                    try:
                        for status in self.client.register(store):
                            if status == WebOSClient.PROMPTED:
                                raise TVAuthenticationError(
                                    "Stored key rejected. Please run 'lgtv pair' again."
                                )
                            elif status == WebOSClient.REGISTERED:
                                break
                    except Exception as e:
                        raise TVAuthenticationError(f"Authentication failed: {e}")

                # Connection successful
                return

            except ConnectionRefusedError as e:
                last_error = e
                continue
            except (OSError, Exception) as e:
                # Connection reset by peer, etc.
                last_error = e
                if "Connection reset by peer" in str(e) or "Errno 54" in str(e):
                    continue  # Try the other connection type
                # For other errors, don't retry
                break

        # Both connection attempts failed
        if last_error:
            if isinstance(last_error, ConnectionRefusedError):
                raise TVConnectionError(
                    f"Connection refused by TV at {self.ip}. "
                    "Make sure 'LG Connect Apps' is enabled in Network settings."
                )
            elif "Connection reset by peer" in str(last_error) or "Errno 54" in str(last_error):
                raise TVConnectionError(
                    f"Connection reset by TV at {self.ip}.\n"
                    "Please check:\n"
                    "  1. TV is on and connected to network\n"
                    "  2. 'LG Connect Apps' is enabled in TV Settings → Network → LG Connect Apps\n"
                    "  3. TV firmware is up to date"
                )
            elif isinstance(last_error, TimeoutError):
                raise TVConnectionError(
                    f"Connection timeout to TV at {self.ip}. "
                    "Check that the TV is on and reachable."
                )
            else:
                raise TVConnectionError(f"Failed to connect to TV: {last_error}")

    def pair(self) -> str:
        """Initiate pairing with the TV.

        Returns:
            The pairing key

        Raises:
            TVAuthenticationError: If pairing fails
        """
        try:
            store = {}
            for status in self.client.register(store):
                if status == WebOSClient.PROMPTED:
                    print(f"Please accept the pairing request on your TV at {self.ip}...")
                elif status == WebOSClient.REGISTERED:
                    key = store.get("client_key")
                    if not key:
                        raise TVAuthenticationError("Pairing succeeded but no key received")
                    return key

            raise TVAuthenticationError("Pairing failed")

        except Exception as e:
            raise TVAuthenticationError(f"Pairing failed: {e}")

    @property
    def system(self) -> SystemControl:
        """Get system control interface."""
        if self._system is None:
            self._system = SystemControl(self.client)
        return self._system

    @property
    def media(self) -> MediaControl:
        """Get media control interface."""
        if self._media is None:
            self._media = MediaControl(self.client)
        return self._media

    @property
    def app(self) -> ApplicationControl:
        """Get application control interface."""
        if self._app is None:
            self._app = ApplicationControl(self.client)
        return self._app

    @property
    def input(self) -> InputControl:
        """Get input control interface."""
        if self._input is None:
            self._input = InputControl(self.client)
        return self._input

    @property
    def tv(self) -> TvControl:
        """Get TV control interface."""
        if self._tv is None:
            self._tv = TvControl(self.client)
        return self._tv

    @property
    def source(self) -> SourceControl:
        """Get source control interface."""
        if self._source is None:
            self._source = SourceControl(self.client)
        return self._source

    def disconnect(self):
        """Disconnect from the TV."""
        if self.client:
            try:
                self.client.close()
            except:
                pass

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
        return False
