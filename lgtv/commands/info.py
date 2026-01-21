"""Info and system information commands."""

import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, info as info_msg


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def info():
    """System information commands."""
    pass


@info.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def system(config_obj, tv, ip):
    """Get system information."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            system_info = controller.system.info()

            if not system_info:
                info_msg("System information unavailable")
                return

            # Handle both camelCase and snake_case keys
            model = system_info.get('modelName') or system_info.get('model_name', 'Unknown')
            webos = system_info.get('sdkVersion') or system_info.get('product_name', 'Unknown')

            # Firmware from major.minor version or firmwareRevision
            major_ver = system_info.get('major_ver', '')
            minor_ver = system_info.get('minor_ver', '')
            if major_ver and minor_ver:
                firmware = f"{major_ver}.{minor_ver}"
            else:
                firmware = system_info.get('firmwareRevision')

            click.echo("System Information:")
            click.echo(f"  Model: {model}")
            click.echo(f"  webOS Version: {webos}")

            if firmware:
                click.echo(f"  Firmware: {firmware}")

            uhd = system_info.get("UHD") or system_info.get("uhd")
            if uhd:
                click.echo(f"  UHD: {uhd}")

            product = system_info.get("productName") or system_info.get("product_name")
            if product:
                click.echo(f"  Product: {product}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to get system info: {e}")


@info.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def current(config_obj, tv, ip):
    """Get current TV state (app, channel, input)."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            click.echo("Current TV State:\n")

            # Current app
            try:
                app_info = controller.app.get_current()
                if app_info:
                    # Handle both dict and object responses
                    if isinstance(app_info, dict):
                        title = app_info.get("title", app_info.get("appId", "Unknown"))
                        app_id = app_info.get("appId", app_info.get("id", ""))
                    elif hasattr(app_info, "data") and isinstance(app_info.data, dict):
                        title = app_info.data.get("title", app_info.data.get("appId", "Unknown"))
                        app_id = app_info.data.get("appId", app_info.data.get("id", ""))
                    else:
                        title = getattr(app_info, "title", getattr(app_info, "appId", "Unknown"))
                        app_id = getattr(app_info, "appId", getattr(app_info, "id", ""))
                    click.echo(f"Application: {title} ({app_id})")
            except:
                click.echo("Application: Unable to retrieve")

            # Current channel (if in TV mode)
            try:
                channel = controller.tv.get_current_channel()
                if channel:
                    ch_num = channel.get("channelNumber", "?")
                    ch_name = channel.get("channelName", "Unknown")
                    click.echo(f"Channel: {ch_num} - {ch_name}")
            except:
                pass

            # Volume
            try:
                vol_info = controller.media.get_volume()
                if vol_info:
                    # Handle both dict and object responses
                    if isinstance(vol_info, dict):
                        # Check for nested volumeStatus
                        if "volumeStatus" in vol_info:
                            volume = vol_info["volumeStatus"].get("volume", "?")
                            muted = vol_info["volumeStatus"].get("muteStatus", False)
                        else:
                            volume = vol_info.get("volume", "?")
                            muted = vol_info.get("muted", vol_info.get("muteStatus", False))
                    elif hasattr(vol_info, "data") and isinstance(vol_info.data, dict):
                        if "volumeStatus" in vol_info.data:
                            volume = vol_info.data["volumeStatus"].get("volume", "?")
                            muted = vol_info.data["volumeStatus"].get("muteStatus", False)
                        else:
                            volume = vol_info.data.get("volume", "?")
                            muted = vol_info.data.get("muted", vol_info.data.get("muteStatus", False))
                    elif hasattr(vol_info, "volume"):
                        volume = getattr(vol_info, "volume", "?")
                        muted = getattr(vol_info, "muted", getattr(vol_info, "muteStatus", False))
                    else:
                        volume = "?"
                        muted = False

                    muted_text = " (MUTED)" if muted else ""
                    click.echo(f"Volume: {volume}{muted_text}")
            except:
                pass

            # Audio output
            try:
                audio = controller.media.get_audio_output()
                if audio:
                    # Handle both dict and object responses
                    if isinstance(audio, dict):
                        output = audio.get("soundOutput", "Unknown")
                    elif hasattr(audio, "data") and isinstance(audio.data, dict):
                        output = audio.data.get("soundOutput", "Unknown")
                    elif hasattr(audio, "soundOutput"):
                        output = getattr(audio, "soundOutput", "Unknown")
                    else:
                        output = str(audio)
                    click.echo(f"Audio Output: {output}")
            except:
                pass

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to get current state: {e}")
