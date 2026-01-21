"""Power control commands."""

import time
import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, success, info, warning, wake_on_lan


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def power():
    """Power management commands."""
    pass


@power.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def on(config_obj, tv, ip):
    """Turn TV on using Wake-on-LAN."""
    try:
        # Get TV configuration
        if not ip:
            tv_config = config_obj.get_tv(tv)
            if not tv_config:
                error("No TV configured. Use 'lgtv pair <ip>' to add a TV.")
                return

            ip = tv_config["ip"]
            mac = tv_config.get("mac")

            if not mac:
                error(
                    "MAC address not configured for this TV. "
                    "Wake-on-LAN requires the TV's MAC address.\n"
                    f"Please add it to the configuration file: {config_obj.config_path}"
                )
                return
        else:
            mac = None
            warning("Using direct IP without configuration. MAC address needed for Wake-on-LAN.")

        if mac:
            info(f"Sending Wake-on-LAN packet to {mac}...")
            wake_on_lan(mac, ip=ip)
            success("Wake-on-LAN packet sent. TV should power on shortly.")

            # Wait a bit and try to verify connection
            info("Waiting for TV to respond...")
            time.sleep(5)

            try:
                with TVController(config_obj, tv_name=tv, ip=ip, timeout=5):
                    success("TV is now online and responsive")
            except:
                warning("TV did not respond yet. It may still be starting up.")
        else:
            error("Cannot power on without MAC address")

    except Exception as e:
        error(str(e))


@power.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def off(config_obj, tv, ip):
    """Turn TV off."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.system.power_off()
            success("TV powered off")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to power off TV: {e}")


@power.command("screen-off")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def screen_off(config_obj, tv, ip):
    """Turn screen off (energy saving mode)."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.system.screen_off()
            success("Screen turned off")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to turn screen off: {e}")


@power.command("screen-on")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def screen_on(config_obj, tv, ip):
    """Turn screen on."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.system.screen_on()
            success("Screen turned on")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to turn screen on: {e}")


@power.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def status(config_obj, tv, ip):
    """Get power status."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Try to get system info as a connectivity check
            system_info = controller.system.info()
            success("TV is ON and responsive")

            # Show some basic info
            if system_info:
                model = system_info.get("modelName", "Unknown")
                version = system_info.get("sdkVersion", "Unknown")
                info(f"Model: {model}")
                info(f"webOS Version: {version}")

    except TVConnectionError:
        info("TV is OFF or unreachable")
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to get power status: {e}")
