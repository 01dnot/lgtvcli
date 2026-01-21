"""Main CLI interface for LG TV control."""

import click
from .config import Config
from .tv import TVController, TVConnectionError, TVAuthenticationError
from .discovery import discover_tvs
from .utils import error, success, info, warning, wake_on_lan
from . import commands


# Global options that can be passed to all commands
pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group(invoke_without_command=True)
@click.version_option()
@click.pass_context
def main(ctx):
    """LG TV CLI - Control your LG WebOS TV from the command line."""
    ctx.obj = Config()

    # Show help if no command is provided
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


# Import and register command groups
from .commands import power, volume, apps, input_cmd, media, info, control, discover_features


# Register command groups
main.add_command(power.power)
main.add_command(volume.volume)
main.add_command(volume.audio)
main.add_command(apps.app)
main.add_command(input_cmd.input)
main.add_command(input_cmd.channel)
main.add_command(media.media)
main.add_command(info.info)
main.add_command(control.button)
main.add_command(control.notify)
main.add_command(control.keyboard)
main.add_command(control.mouse)
main.add_command(control.inspect)
main.add_command(discover_features.discover_features)


@main.group()
@pass_config
def config(config_obj):
    """Manage TV configurations."""
    pass


@config.command("list")
@pass_config
def config_list(config_obj):
    """List all configured TVs."""
    tvs = config_obj.list_tvs()
    default = config_obj.get_default_tv()

    if not tvs:
        info("No TVs configured. Use 'lgtv pair <ip>' to add a TV.")
        return

    click.echo("Configured TVs:")
    for name, tv_info in tvs.items():
        marker = " (default)" if name == default else ""
        click.echo(f"  {name}{marker}")
        click.echo(f"    IP: {tv_info['ip']}")
        if tv_info.get("mac"):
            click.echo(f"    MAC: {tv_info['mac']}")
        if tv_info.get("model"):
            click.echo(f"    Model: {tv_info['model']}")
        click.echo()


@config.command("set-default")
@click.argument("name")
@pass_config
def config_set_default(config_obj, name):
    """Set the default TV."""
    try:
        config_obj.set_default_tv(name)
        success(f"Default TV set to: {name}")
    except ValueError as e:
        error(str(e))


@config.command("remove")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to remove this TV?")
@pass_config
def config_remove(config_obj, name):
    """Remove a TV from configuration."""
    config_obj.remove_tv(name)
    success(f"TV '{name}' removed from configuration")


@main.command()
@click.option("--timeout", "-t", default=5, help="Discovery timeout in seconds")
def discover(timeout):
    """Discover LG TVs on the local network."""
    click.echo("Searching for LG TVs on the network...")

    tvs = discover_tvs(timeout)

    if not tvs:
        warning("No LG TVs found on the network.")
        click.echo("\nTroubleshooting:")
        click.echo("  - Make sure your TV is on")
        click.echo("  - Enable 'LG Connect Apps' in TV Settings > Network")
        click.echo("  - Ensure your computer and TV are on the same network")
        click.echo("\nIf your TV is not discovered, you can pair manually:")
        click.echo("  lgtv pair <ip-address>")
        return

    click.echo(f"\nFound {len(tvs)} TV(s):\n")
    for i, tv in enumerate(tvs, 1):
        click.echo(f"{i}. IP: {tv['ip']}")
        if tv.get("name"):
            click.echo(f"   Name: {tv['name']}")
        if tv.get("model"):
            click.echo(f"   Model: {tv['model']}")
        click.echo(f"   Discovery method: {tv.get('discovery_method', 'unknown')}")
        click.echo()

    click.echo("To pair with a TV, run:")
    click.echo(f"  lgtv pair {tvs[0]['ip']}")


@main.command()
@click.argument("ip")
@click.option("--name", "-n", help="Friendly name for the TV")
@pass_config
def pair(config_obj, ip, name):
    """Pair with a TV and save configuration."""
    if not name:
        name = click.prompt("Enter a name for this TV", default=ip.replace(".", "-"))

    try:
        click.echo(f"Connecting to TV at {ip}...")

        # Create TV controller without stored key for pairing
        controller = TVController(config_obj, ip=ip)

        # Initiate pairing
        click.echo("Initiating pairing...")
        key = controller.pair()

        click.echo("Pairing successful!")

        # Get system info to get MAC address and model
        try:
            system_info = controller.system.info()
            model = system_info.get("modelName", None)

            # Try to get MAC address from network info
            mac = None
            # Note: PyWebOSTV doesn't directly expose MAC, would need additional SSAP call
            # For now, we'll leave it None and user can add it manually if needed for WoL

        except:
            model = None
            mac = None

        # Save configuration
        config_obj.add_tv(name, ip, mac=mac, key=key, model=model)

        success(f"TV '{name}' paired and saved to configuration")

        if not mac:
            click.echo("\nNote: MAC address not detected. If you want to use 'lgtv power on',")
            click.echo("you'll need to find your TV's MAC address and add it manually to:")
            click.echo(f"  {config_obj.config_path}")

        controller.disconnect()

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
