"""Volume and audio control commands."""

import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, success, info, format_volume_info


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def volume():
    """Volume control commands."""
    pass


@volume.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def up(config_obj, tv, ip):
    """Increase volume by 1."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.volume_up()
            # Get current volume to display
            vol_info = controller.media.get_volume()
            success("Volume increased")
            if vol_info:
                info(format_volume_info(vol_info))

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to increase volume: {e}")


@volume.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def down(config_obj, tv, ip):
    """Decrease volume by 1."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.volume_down()
            # Get current volume to display
            vol_info = controller.media.get_volume()
            success("Volume decreased")
            if vol_info:
                info(format_volume_info(vol_info))

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to decrease volume: {e}")


@volume.command()
@click.argument("level", type=click.IntRange(0, 100))
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def set(config_obj, level, tv, ip):
    """Set volume to specific level (0-100)."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.set_volume(level)
            success(f"Volume set to {level}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to set volume: {e}")


@volume.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def mute(config_obj, tv, ip):
    """Toggle mute."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Get current mute status
            vol_info = controller.media.get_volume()

            # Extract mute status from nested structure
            if vol_info:
                if isinstance(vol_info, dict):
                    if "volumeStatus" in vol_info:
                        current_mute = vol_info["volumeStatus"].get("muteStatus", False)
                    else:
                        current_mute = vol_info.get("muted", vol_info.get("muteStatus", False))
                elif hasattr(vol_info, "data") and isinstance(vol_info.data, dict):
                    if "volumeStatus" in vol_info.data:
                        current_mute = vol_info.data["volumeStatus"].get("muteStatus", False)
                    else:
                        current_mute = vol_info.data.get("muted", vol_info.data.get("muteStatus", False))
                else:
                    current_mute = False
            else:
                current_mute = False

            # Toggle mute
            controller.media.mute(not current_mute)

            if current_mute:
                success("Unmuted")
            else:
                success("Muted")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to toggle mute: {e}")


@volume.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@click.option("--debug", is_flag=True, help="Show debug information")
@pass_config
def status(config_obj, tv, ip, debug):
    """Get current volume status."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            vol_info = controller.media.get_volume()

            if debug:
                click.echo(f"DEBUG: Type: {type(vol_info)}")
                click.echo(f"DEBUG: Dir: {dir(vol_info)}")
                click.echo(f"DEBUG: Repr: {repr(vol_info)}")
                if hasattr(vol_info, '__dict__'):
                    click.echo(f"DEBUG: __dict__: {vol_info.__dict__}")
                if hasattr(vol_info, 'data'):
                    click.echo(f"DEBUG: .data: {vol_info.data}")

            if vol_info:
                info(format_volume_info(vol_info))
            else:
                warning("Could not retrieve volume information")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to get volume status: {e}")


@click.group()
def audio():
    """Audio output control commands."""
    pass


@audio.command("list")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def audio_list(config_obj, tv, ip):
    """List available audio output sources."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            sources = controller.media.list_audio_output_sources()

            if not sources:
                info("No audio output sources available")
                return

            current = controller.media.get_audio_output()

            # Handle both dict and object responses for current output
            if isinstance(current, dict):
                current_id = current.get("soundOutput")
            elif hasattr(current, "data") and isinstance(current.data, dict):
                current_id = current.data.get("soundOutput")
            elif hasattr(current, "soundOutput"):
                current_id = getattr(current, "soundOutput", None)
            else:
                current_id = None

            click.echo("Available audio outputs:")
            for source in sources:
                # Handle both dict and object responses for sources
                if isinstance(source, dict):
                    source_id = source.get("soundOutput", "")
                elif hasattr(source, "data") and isinstance(source.data, dict):
                    source_id = source.data.get("soundOutput", "")
                elif hasattr(source, "soundOutput"):
                    source_id = getattr(source, "soundOutput", "")
                else:
                    source_id = str(source)

                marker = " (current)" if source_id == current_id else ""
                click.echo(f"  {source_id}{marker}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to list audio outputs: {e}")


@audio.command("set")
@click.argument("output")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def audio_set(config_obj, output, tv, ip):
    """Set audio output source (e.g., tv_speaker, external_optical, bt_soundbar)."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.set_audio_output(output)
            success(f"Audio output set to: {output}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to set audio output: {e}")


@audio.command("status")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def audio_status(config_obj, tv, ip):
    """Get current audio output."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            output = controller.media.get_audio_output()
            if output:
                # Handle both dict and object responses
                if isinstance(output, dict):
                    sound_output = output.get("soundOutput", "Unknown")
                elif hasattr(output, "data") and isinstance(output.data, dict):
                    sound_output = output.data.get("soundOutput", "Unknown")
                elif hasattr(output, "soundOutput"):
                    sound_output = getattr(output, "soundOutput", "Unknown")
                else:
                    sound_output = str(output)

                info(f"Current audio output: {sound_output}")
            else:
                warning("Could not retrieve audio output information")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to get audio output: {e}")
