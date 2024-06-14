import logging
import os
import sys
from pathlib import Path
import typing as t

import click

from antares_web_installer.app import App, InstallError

if os.name == "posix":
    TARGET_DIR = "/opt/antares-web/"
else:
    TARGET_DIR = "C:/Program Files/AntaresWeb/"
SRC_DIR = Path(".")

logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "-s",
    "--source-dir",
    "src_dir",
    default=SRC_DIR,
    show_default=True,
    type=click.Path(),
    help="Where to find the Antares Web sources.",
)
@click.option(
    "-t",
    "--target-dir",
    default=TARGET_DIR,
    show_default=True,
    type=click.Path(),
    help="Target location of Antares Web Server.",
)
@click.option(
    "--shortcut/--no-shortcut",
    default=True,
    show_default=True,
    help="Create a shortcut on desktop.",
)
@click.option(
    "--launch/--no-launch",
    default=True,
    show_default=True,
    help="Launch Antares Web Server.",
)
@click.option(
    "--browser/--no-browser",
    default=True,
    show_default=True,
    help="Open user's default browser at the Antares Web Server home page.",
)
def install_cli(src_dir: t.Union[str, Path], target_dir: t.Union[str, Path], **kwargs) -> None:
    """
    Install Antares Web Server sources.
    Takes two positional argument : 'src_dir' source directory to copy files from and 'target' directory
    to paste files to.
    """
    target_dir = Path(target_dir).expanduser()
    src_dir = Path(src_dir)

    logging.basicConfig(level=logging.INFO, format="[%(asctime)-15s] %(message)s", stream=sys.stdout)

    logger.info(f"Starting installation in directory: '{target_dir}'...")
    app = App(source_dir=src_dir, target_dir=target_dir, **kwargs)
    try:
        app.run()
    except InstallError as e:
        # Display only the error message without traceback
        logger.error(e)
        raise SystemExit(1)
    except KeyboardInterrupt:
        logger.error("Installation interrupted.")
        raise SystemExit(1)

    logger.info("Done.")
