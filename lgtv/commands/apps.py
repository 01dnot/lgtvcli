"""Application management commands."""

import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, success, info, warning, format_app_info, find_app_by_name


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def app():
    """Application management commands."""
    pass


@app.command("list")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@click.option("--debug", is_flag=True, help="Show debug information")
@pass_config
def app_list(config_obj, tv, ip, debug):
    """List installed applications."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            apps = controller.app.list_apps()

            if not apps:
                info("No applications found")
                return

            # Convert to list of dicts if needed (handle both dict and object responses)
            app_dicts = []
            for app_info in apps:
                if isinstance(app_info, dict):
                    app_dicts.append(app_info)
                elif hasattr(app_info, 'data') and isinstance(app_info.data, dict):
                    # PyWebOSTV Application object with .data attribute
                    app_dicts.append(app_info.data)
                else:
                    # Fallback for unknown object types
                    app_id = ""
                    title = "Unknown"

                    # Try to get ID
                    for id_attr in ["id", "appId", "app_id"]:
                        if hasattr(app_info, id_attr):
                            app_id = getattr(app_info, id_attr, "")
                            if app_id:
                                break

                    # Try to get title
                    for title_attr in ["title", "name", "label", "appName"]:
                        if hasattr(app_info, title_attr):
                            title = getattr(app_info, title_attr, "Unknown")
                            if title and title != "Unknown":
                                break

                    app_dicts.append({
                        "id": app_id,
                        "title": title,
                    })

            # Sort by title
            app_dicts.sort(key=lambda x: x.get("title", x.get("name", "")))

            click.echo(f"Installed applications ({len(app_dicts)}):\n")
            for app_info in app_dicts:
                title = app_info.get("title", app_info.get("name", "Unknown"))
                app_id = app_info.get("id", "")
                if title != "Unknown" or app_id:  # Only show if we have real data
                    click.echo(f"  {title}")
                    click.echo(f"    ID: {app_id}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to list applications: {e}")


@app.command("launch")
@click.argument("name")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@click.option("--debug", is_flag=True, help="Show debug information")
@pass_config
def app_launch(config_obj, name, tv, ip, debug):
    """Launch an application by name."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            # Get list of apps to find the right one
            apps = controller.app.list_apps()

            if not apps:
                error("Could not retrieve app list")
                return

            if debug:
                click.echo(f"DEBUG: Found {len(apps)} apps")
                click.echo(f"DEBUG: First app type: {type(apps[0])}")
                if hasattr(apps[0], 'data'):
                    click.echo(f"DEBUG: First app.data type: {type(apps[0].data)}")

            # Find app by name
            app_info = find_app_by_name(apps, name)

            if debug:
                click.echo(f"DEBUG: app_info type: {type(app_info)}")
                click.echo(f"DEBUG: app_info value: {app_info}")

            if not app_info:
                error(f"Application '{name}' not found. Use 'lgtv app list' to see available apps.")
                return

            # Ensure app_info is a dict
            if not isinstance(app_info, dict):
                error(f"Internal error: app_info is {type(app_info)}, expected dict")
                return

            app_id = app_info.get("id")
            if not app_id:
                error(f"Application found but has no ID: {app_info}")
                return

            title = app_info.get("title", app_info.get("name", name))

            # Launch the app - PyWebOSTV expects the full app dict, not just the ID
            controller.app.launch(app_info)
            success(f"Launched: {title}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to launch application: {e}")


@app.command("current")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def app_current(config_obj, tv, ip):
    """Show current/foreground application."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            app_info = controller.app.get_current()

            if not app_info:
                info("No application currently running or information unavailable")
                return

            # Handle both dict and object responses
            if isinstance(app_info, dict):
                title = app_info.get("title", app_info.get("appId", "Unknown"))
                app_id = app_info.get("appId", app_info.get("id", ""))
                window_id = app_info.get("windowId")
            elif hasattr(app_info, "data") and isinstance(app_info.data, dict):
                title = app_info.data.get("title", app_info.data.get("appId", "Unknown"))
                app_id = app_info.data.get("appId", app_info.data.get("id", ""))
                window_id = app_info.data.get("windowId")
            else:
                title = getattr(app_info, "title", getattr(app_info, "appId", "Unknown"))
                app_id = getattr(app_info, "appId", getattr(app_info, "id", ""))
                window_id = getattr(app_info, "windowId", None)

            click.echo("Current application:")
            click.echo(f"  Title: {title}")
            click.echo(f"  ID: {app_id}")

            # Show additional info if available
            if window_id:
                click.echo(f"  Window ID: {window_id}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to get current application: {e}")


@app.command("close")
@click.argument("app_id")
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def app_close(config_obj, app_id, tv, ip):
    """Close an application by ID."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.app.close({"id": app_id})
            success(f"Closed application: {app_id}")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to close application: {e}")
