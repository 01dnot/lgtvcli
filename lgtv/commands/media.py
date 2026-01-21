"""Media playback control commands."""

import click
from ..config import Config
from ..tv import TVController, TVConnectionError, TVAuthenticationError
from ..utils import error, success


pass_config = click.make_pass_decorator(Config, ensure=True)


@click.group()
def media():
    """Media playback control commands."""
    pass


@media.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def play(config_obj, tv, ip):
    """Start playback."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.play()
            success("Playback started")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to start playback: {e}")


@media.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def pause(config_obj, tv, ip):
    """Pause playback."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.pause()
            success("Playback paused")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to pause playback: {e}")


@media.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def stop(config_obj, tv, ip):
    """Stop playback."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.stop()
            success("Playback stopped")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to stop playback: {e}")


@media.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def rewind(config_obj, tv, ip):
    """Rewind playback."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.rewind()
            success("Rewinding")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to rewind: {e}")


@media.command()
@click.option("--tv", help="Name of configured TV")
@click.option("--ip", help="TV IP address (bypass config)")
@pass_config
def forward(config_obj, tv, ip):
    """Fast forward playback."""
    try:
        with TVController(config_obj, tv_name=tv, ip=ip) as controller:
            controller.media.fast_forward()
            success("Fast forwarding")

    except TVConnectionError as e:
        error(str(e))
    except TVAuthenticationError as e:
        error(str(e))
    except Exception as e:
        error(f"Failed to fast forward: {e}")
