"""Input and channel control commands."""

import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, success, info, warning


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def input():
    """Input source control commands."""
    pass


@input.command("list")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def input_list(config_obj, tv, ip):
    """List available input sources."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            sources = controller.source.list_sources()

            if not sources:
                info("No input sources found")
                return

            click.echo("Available input sources:\n")
            for source in sources:
                source_id = source.get("id", "")
                label = source.get("label", source_id)
                connected = source.get("connected", False)
                status = " (connected)" if connected else ""

                click.echo(f"  {source_id}")
                click.echo(f"    Label: {label}{status}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to list input sources: {e}")


@input.command("set")
@click.argument("source_id")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def input_set(config_obj, source_id, tv, ip):
    """Set input source (e.g., HDMI_1, HDMI_2)."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.source.set_source(source_id)
            success(f"Switched to input: {source_id}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to set input source: {e}")


@click.group()
def channel():
    """TV channel control commands."""
    pass


@channel.command("up")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def channel_up(config_obj, tv, ip):
    """Go to next channel."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.tv.channel_up()
            success("Channel up")

            # Try to show current channel
            try:
                current = controller.tv.get_current_channel()
                if current:
                    channel_name = current.get("channelName", "")
                    channel_num = current.get("channelNumber", "")
                    if channel_name or channel_num:
                        info(f"Current: {channel_num} - {channel_name}")
            except:
                pass

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to change channel: {e}")


@channel.command("down")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def channel_down(config_obj, tv, ip):
    """Go to previous channel."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.tv.channel_down()
            success("Channel down")

            # Try to show current channel
            try:
                current = controller.tv.get_current_channel()
                if current:
                    channel_name = current.get("channelName", "")
                    channel_num = current.get("channelNumber", "")
                    if channel_name or channel_num:
                        info(f"Current: {channel_num} - {channel_name}")
            except:
                pass

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to change channel: {e}")


@channel.command("set")
@click.argument("channel_number")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def channel_set(config_obj, channel_number, tv, ip):
    """Set specific channel by number."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Get channel list to find the channel ID
            channels = controller.tv.channel_list()

            if not channels:
                error("Could not retrieve channel list")
                return

            # Find channel by number
            target_channel = None
            for ch in channels:
                if ch.get("channelNumber") == channel_number:
                    target_channel = ch
                    break

            if not target_channel:
                error(f"Channel {channel_number} not found")
                return

            channel_id = target_channel.get("channelId")
            controller.tv.set_channel_with_id(channel_id)
            success(f"Switched to channel {channel_number}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to set channel: {e}")


@channel.command("list")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def channel_list(config_obj, tv, ip):
    """List available channels."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            channels = controller.tv.channel_list()

            if not channels:
                info("No channels found or TV not in TV mode")
                return

            click.echo(f"Available channels ({len(channels)}):\n")
            for ch in channels:
                ch_num = ch.get("channelNumber", "?")
                ch_name = ch.get("channelName", "Unknown")
                click.echo(f"  {ch_num} - {ch_name}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to list channels: {e}")


@channel.command("info")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def channel_info(config_obj, tv, ip):
    """Get current channel and program information."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            current = controller.tv.get_current_channel()

            if not current:
                info("Not watching TV or information unavailable")
                return

            click.echo("Current channel:")
            if current.get("channelNumber"):
                click.echo(f"  Number: {current['channelNumber']}")
            if current.get("channelName"):
                click.echo(f"  Name: {current['channelName']}")

            # Try to get program info
            try:
                program = controller.tv.get_current_program()
                if program:
                    click.echo("\nCurrent program:")
                    if program.get("programName"):
                        click.echo(f"  Title: {program['programName']}")
                    if program.get("startTime"):
                        click.echo(f"  Start: {program['startTime']}")
                    if program.get("endTime"):
                        click.echo(f"  End: {program['endTime']}")
            except:
                pass

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to get channel info: {e}")
