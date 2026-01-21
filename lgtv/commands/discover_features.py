"""Discover additional TV features and services."""

import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, info


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def discover_features(config_obj, tv, ip):
    """Discover available TV services and capabilities."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            click.echo("Querying TV for available services...\n")

            # Try to get service list via SSAP
            try:
                # Use the underlying client to make a direct SSAP request
                response = controller.client.request("ssap://api/getServiceList")

                if response and "services" in response:
                    services = response["services"]
                    click.echo(f"Found {len(services)} available services:\n")

                    # Group services by category
                    categories = {}
                    for service in services:
                        name = service.get("name", "unknown")
                        version = service.get("version", "?")

                        # Extract category from service name
                        if "." in name:
                            category = name.split(".")[0]
                        else:
                            category = "other"

                        if category not in categories:
                            categories[category] = []

                        categories[category].append(f"{name} (v{version})")

                    # Display by category
                    for category, service_list in sorted(categories.items()):
                        click.echo(f"\n{category.upper()}:")
                        for svc in sorted(service_list):
                            click.echo(f"  - {svc}")
                else:
                    info("Service list not available from this TV")

            except Exception as e:
                info(f"Could not retrieve service list: {e}")

            # Show what we've implemented
            click.echo("\n" + "="*60)
            click.echo("IMPLEMENTED FEATURES IN lgtv CLI:")
            click.echo("="*60)

            features = {
                "Power Control": ["power on/off", "screen on/off", "Wake-on-LAN"],
                "Volume & Audio": ["volume control", "mute toggle", "audio output selection"],
                "Applications": ["list apps", "launch apps", "close apps", "get current app"],
                "Input & Channels": ["switch inputs", "channel navigation", "channel list", "program info"],
                "Media Playback": ["play", "pause", "stop", "rewind", "fast forward"],
                "Remote Control": ["navigation buttons", "number keys", "color buttons"],
                "Input Devices": ["keyboard input", "mouse/pointer control"],
                "System Info": ["system info", "current state", "detailed inspection"],
                "Notifications": ["toast notifications"],
            }

            for category, items in features.items():
                click.echo(f"\n{category}:")
                for item in items:
                    click.echo(f"  ✓ {item}")

            # Show known limitations
            click.echo("\n" + "="*60)
            click.echo("KNOWN LIMITATIONS:")
            click.echo("="*60)
            click.echo("\n❌ Not available via external API:")
            click.echo("  - Screenshot capture")
            click.echo("  - HTML/DOM access")
            click.echo("  - Picture settings (brightness, contrast, etc.)")
            click.echo("  - 3D mode control")
            click.echo("\n💡 These features require LG Developer Tools or")
            click.echo("   are not exposed in the PyWebOSTV library.")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to discover features: {e}")
