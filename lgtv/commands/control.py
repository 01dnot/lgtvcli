"""Remote control and notification commands."""

import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, success, info as info_msg


pass_config = click.make_pass_decorator(Config, ensure=True)


VALID_BUTTONS = [
    "home", "back", "up", "down", "left", "right", "ok", "enter",
    "menu", "info", "exit", "dash",
    "red", "green", "yellow", "blue",
    "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
    "asterisk", "cc",
]


@click.command()
@click.argument("button_name", type=click.Choice(VALID_BUTTONS, case_sensitive=False))
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def button(config_obj, button_name, tv, ip):
    """Send remote control button press.

    Available buttons: home, back, up, down, left, right, ok, enter,
    menu, info, exit, dash, red, green, yellow, blue, 0-9, asterisk, cc
    """
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Connect input socket for button commands
            controller.input.connect_input()

            # Map button names to InputControl methods
            button_lower = button_name.lower()

            if button_lower == "home":
                controller.input.home()
            elif button_lower == "back":
                controller.input.back()
            elif button_lower == "up":
                controller.input.up()
            elif button_lower == "down":
                controller.input.down()
            elif button_lower == "left":
                controller.input.left()
            elif button_lower == "right":
                controller.input.right()
            elif button_lower in ("ok", "enter"):
                controller.input.ok()
            elif button_lower == "menu":
                controller.input.menu()
            elif button_lower == "info":
                controller.input.info()
            elif button_lower == "exit":
                controller.input.exit()
            elif button_lower == "dash":
                controller.input.dash()
            elif button_lower == "red":
                controller.input.red()
            elif button_lower == "green":
                controller.input.green()
            elif button_lower == "yellow":
                controller.input.yellow()
            elif button_lower == "blue":
                controller.input.blue()
            elif button_lower == "asterisk":
                controller.input.asterisk()
            elif button_lower == "cc":
                controller.input.cc()
            elif button_lower.isdigit():
                # Number buttons
                num = int(button_lower)
                getattr(controller.input, f"num_{num}")()
            else:
                error(f"Button '{button_name}' not implemented")
                return

            success(f"Button pressed: {button_name}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to send button press: {e}")


@click.command()
@click.argument("message")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def notify(config_obj, message, tv, ip):
    """Show notification message on TV."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.system.notify(message)
            success(f"Notification sent: {message}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to send notification: {e}")


@click.command()
@click.argument("text")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def keyboard(config_obj, text, tv, ip):
    """Send keyboard input to TV.

    Note: The keyboard must be visible on screen for this to work.
    Use this to type text into input fields on the TV.
    """
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Connect input socket for keyboard input
            controller.input.connect_input()
            controller.input.type(text)
            success(f"Typed: {text}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to send keyboard input: {e}")


@click.group()
def mouse():
    """Mouse/pointer control commands."""
    pass


@mouse.command()
@click.argument("dx", type=int)
@click.argument("dy", type=int)
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def move(config_obj, dx, dy, tv, ip):
    """Move mouse cursor by relative offset (dx, dy)."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Connect input socket for mouse control
            controller.input.connect_input()
            controller.input.move(dx, dy)
            success(f"Moved cursor by ({dx}, {dy})")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to move cursor: {e}")


@mouse.command("click")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def mouse_click(config_obj, tv, ip):
    """Send mouse click."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Connect input socket for mouse control
            controller.input.connect_input()
            controller.input.click()
            success("Mouse clicked")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to click: {e}")


@click.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def inspect(config_obj, tv, ip):
    """Get detailed TV state (experimental).

    Note: Screenshot and HTML/DOM access are not available through the
    LG WebOS external API. This command shows available state information.
    """
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            click.echo("TV State Inspection:\n")

            # System info
            click.echo("=== System ===")
            try:
                system_info = controller.system.info()

                if system_info:
                    # Handle both dict and object responses
                    if isinstance(system_info, dict):
                        # Try both camelCase and snake_case keys
                        model = system_info.get('modelName') or system_info.get('model_name', 'Unknown')
                        webos = system_info.get('sdkVersion') or system_info.get('product_name', 'Unknown')
                        # Firmware from major.minor version or firmwareRevision
                        major_ver = system_info.get('major_ver', '')
                        minor_ver = system_info.get('minor_ver', '')
                        if major_ver and minor_ver:
                            firmware = f"{major_ver}.{minor_ver}"
                        else:
                            firmware = system_info.get('firmwareRevision', 'Unknown')
                    elif hasattr(system_info, "data") and isinstance(system_info.data, dict):
                        model = system_info.data.get('modelName') or system_info.data.get('model_name', 'Unknown')
                        webos = system_info.data.get('sdkVersion') or system_info.data.get('product_name', 'Unknown')
                        major_ver = system_info.data.get('major_ver', '')
                        minor_ver = system_info.data.get('minor_ver', '')
                        if major_ver and minor_ver:
                            firmware = f"{major_ver}.{minor_ver}"
                        else:
                            firmware = system_info.data.get('firmwareRevision', 'Unknown')
                    else:
                        model = getattr(system_info, 'modelName', getattr(system_info, 'model_name', 'Unknown'))
                        webos = getattr(system_info, 'sdkVersion', getattr(system_info, 'product_name', 'Unknown'))
                        firmware = getattr(system_info, 'firmwareRevision', 'Unknown')

                    click.echo(f"Model: {model}")
                    click.echo(f"webOS: {webos}")
                    click.echo(f"Firmware: {firmware}")
            except Exception as e:
                click.echo(f"Unable to retrieve system info: {e}")

            # Current app
            click.echo("\n=== Application ===")
            try:
                app_info = controller.app.get_current()
                if app_info:
                    # Handle both dict and object responses
                    if isinstance(app_info, str):
                        # Just an app ID string
                        title = 'Unknown'
                        app_id = app_info
                        window_id = None
                        params = None
                    elif isinstance(app_info, dict):
                        title = app_info.get('title', 'Unknown')
                        app_id = app_info.get('appId', app_info.get('id', 'Unknown'))
                        window_id = app_info.get("windowId")
                        params = app_info.get("params")
                    elif hasattr(app_info, "data") and isinstance(app_info.data, dict):
                        title = app_info.data.get('title', 'Unknown')
                        app_id = app_info.data.get('appId', app_info.data.get('id', 'Unknown'))
                        window_id = app_info.data.get("windowId")
                        params = app_info.data.get("params")
                    else:
                        # Object with attributes (but not a string)
                        title = getattr(app_info, 'title', 'Unknown')
                        app_id = getattr(app_info, 'appId', getattr(app_info, 'id', 'Unknown'))
                        window_id = getattr(app_info, "windowId", None)
                        params = getattr(app_info, "params", None)

                    click.echo(f"Title: {title}")
                    click.echo(f"App ID: {app_id}")
                    if window_id:
                        click.echo(f"Window ID: {window_id}")
                    if params:
                        click.echo(f"Parameters: {params}")
            except:
                click.echo("Unable to retrieve app info")

            # Current channel (if applicable)
            click.echo("\n=== Channel/Source ===")
            try:
                channel = controller.tv.get_current_channel()
                if channel:
                    click.echo(f"Channel: {channel.get('channelNumber', '?')} - {channel.get('channelName', 'Unknown')}")

                    # Try to get program info
                    try:
                        program = controller.tv.get_current_program()
                        if program:
                            click.echo(f"Program: {program.get('programName', 'Unknown')}")
                    except:
                        pass
                else:
                    click.echo("Not in TV mode")
            except:
                click.echo("Unable to retrieve channel info")

            # Audio/Volume
            click.echo("\n=== Audio ===")
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

                audio = controller.media.get_audio_output()
                if audio:
                    # Handle both dict and object responses
                    if isinstance(audio, str):
                        # Just a string value
                        output = audio
                    elif isinstance(audio, dict):
                        output = audio.get('soundOutput', 'Unknown')
                    elif hasattr(audio, "data") and isinstance(audio.data, dict):
                        output = audio.data.get('soundOutput', 'Unknown')
                    elif hasattr(audio, "soundOutput"):
                        output = getattr(audio, "soundOutput", "Unknown")
                    elif type(audio).__name__ == 'AudioOutputSource':
                        # AudioOutputSource object - try to extract the value
                        # The repr shows <AudioOutputSource 'external_arc'>
                        # Try common attribute names
                        output = getattr(audio, 'name', None) or getattr(audio, 'value', None) or str(audio).split("'")[1] if "'" in str(audio) else str(audio)
                    else:
                        output = str(audio)
                    click.echo(f"Audio Output: {output}")
            except:
                click.echo("Unable to retrieve audio info")

            click.echo("\n" + "="*50)
            click.echo("Note: Screenshot and HTML/DOM capture are not supported")
            click.echo("by the LG WebOS external API.")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to inspect TV: {e}")
