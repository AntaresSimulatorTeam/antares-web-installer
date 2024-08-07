import logging
import sys
import typing as t
from pathlib import Path

import click

from antares_web_installer import SRC_DIR, logger
from antares_web_installer.app import App, InstallError


@click.command()
@click.option(
    "-t",
    "--target-dir",
    type=click.Path(),
    help="Target location of Antares Web Server.",
)
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
    "--shortcut/--no-shortcut",
    default=True,
    show_default=True,
    help="Create a shortcut on desktop.",
)
@click.option("--launch/--no-launch", default=True, show_default=True, help="Launch Antares Web Server.")
def install_cli(src_dir: t.Union[str, Path], target_dir: t.Union[str, Path], **kwargs) -> None:
    """
    Install Antares Web Server sources.
    Takes two positional argument : 'src_dir' source directory to copy files from and 'target' directory
    to paste files to.
    """
    target_dir = Path(target_dir).expanduser().absolute()
    src_dir = Path(src_dir).expanduser().absolute()

    cli_logger = logging.StreamHandler()
    cli_logger.setLevel(logging.INFO)
    cli_logger.setFormatter(logging.Formatter("[%(asctime)-15s] %(message)s"))
    logger.addHandler(cli_logger)

    cli_logger.info(f"Starting installation in directory: '{target_dir}'...")
    app = App(source_dir=src_dir, target_dir=target_dir, **kwargs)
    try:
        app.run()
    except InstallError as e:
        # Display only the error message without traceback
        cli_logger.error(e)
        raise SystemExit(1)
    except KeyboardInterrupt:
        cli_logger.error("Installation interrupted.")
        raise SystemExit(1)

    logger.info("Done.")
