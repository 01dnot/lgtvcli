"""Utility functions for LG TV CLI."""

import sys
import click
from wakeonlan import send_magic_packet


def error(message: str, exit_code: int = 1):
    """Print error message and exit.

    Args:
        message: Error message to display
        exit_code: Exit code (default: 1)
    """
    click.secho(f"Error: {message}", fg="red", err=True)
    sys.exit(exit_code)


def success(message: str):
    """Print success message.

    Args:
        message: Success message to display
    """
    click.secho(message, fg="green")


def info(message: str):
    """Print info message.

    Args:
        message: Info message to display
    """
    click.echo(message)


def warning(message: str):
    """Print warning message.

    Args:
        message: Warning message to display
    """
    click.secho(f"Warning: {message}", fg="yellow")


def wake_on_lan(mac_address: str, ip: str = None):
    """Send Wake-on-LAN magic packet to TV.

    Args:
        mac_address: MAC address of the TV
        ip: IP address to send to (optional, uses broadcast if not specified)
    """
    try:
        if ip:
            send_magic_packet(mac_address, ip_address=ip)
        else:
            send_magic_packet(mac_address)
    except Exception as e:
        raise RuntimeError(f"Failed to send Wake-on-LAN packet: {e}")


def format_volume_info(volume_info) -> str:
    """Format volume information for display.

    Args:
        volume_info: Volume information from TV (dict or object)

    Returns:
        Formatted string
    """
    # Handle both dict and object responses
    if isinstance(volume_info, dict):
        # Check if it has nested volumeStatus (LG WebOS format)
        if "volumeStatus" in volume_info:
            volume = volume_info["volumeStatus"].get("volume", "?")
            muted = volume_info["volumeStatus"].get("muteStatus", False)
        else:
            volume = volume_info.get("volume", "?")
            muted = volume_info.get("muted", volume_info.get("muteStatus", False))
    elif hasattr(volume_info, "data") and isinstance(volume_info.data, dict):
        if "volumeStatus" in volume_info.data:
            volume = volume_info.data["volumeStatus"].get("volume", "?")
            muted = volume_info.data["volumeStatus"].get("muteStatus", False)
        else:
            volume = volume_info.data.get("volume", "?")
            muted = volume_info.data.get("muted", volume_info.data.get("muteStatus", False))
    elif hasattr(volume_info, "volume"):
        volume = getattr(volume_info, "volume", "?")
        muted = getattr(volume_info, "muted", getattr(volume_info, "muteStatus", False))
    else:
        volume = "?"
        muted = False

    status = "MUTED" if muted else "UNMUTED"
    return f"Volume: {volume} ({status})"


def format_app_info(app_info: dict) -> str:
    """Format application information for display.

    Args:
        app_info: Application information from TV

    Returns:
        Formatted string
    """
    app_id = app_info.get("id", "")
    title = app_info.get("title", app_info.get("name", "Unknown"))
    return f"{title} ({app_id})"


def find_app_by_name(apps: list, name: str) -> dict:
    """Find app by name (case-insensitive search).

    Args:
        apps: List of app dictionaries or objects
        name: App name to search for

    Returns:
        App dictionary or None if not found
    """
    name_lower = name.lower()

    # Helper to get title from dict or object
    def get_title(app):
        if isinstance(app, dict):
            return app.get("title", app.get("name", ""))
        elif hasattr(app, "data") and isinstance(app.data, dict):
            return app.data.get("title", app.data.get("name", ""))
        else:
            return getattr(app, "title", getattr(app, "name", ""))

    # Helper to convert app to dict
    def to_dict(app):
        if isinstance(app, dict):
            return app
        elif hasattr(app, "data") and isinstance(app.data, dict):
            return app.data
        else:
            return {
                "id": getattr(app, "id", getattr(app, "appId", "")),
                "title": getattr(app, "title", getattr(app, "name", "")),
            }

    # First try exact match
    for app in apps:
        title = get_title(app).lower()
        if title == name_lower:
            return to_dict(app)

    # Then try partial match
    for app in apps:
        title = get_title(app).lower()
        if name_lower in title:
            return to_dict(app)

    return None
