import os
import click
import psutil

from pathlib import Path
import tkinter as tk
from app import App

if os.name == "posix":
    TARGET_DIR = "/opt/antares-web/"
else:
    TARGET_DIR = "C:/Program Files/AntaresWeb/"

SRC_DIR = "."


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
    default=False,
    show_default=True,
    help="Create a shortcut on desktop."
)
@click.option(
    "--launch/--no-launch",
    default=False,
    show_default=True,
    help="Launch Antares Web Server."
)
def install_cli(src_dir: str, target_dir: str, **kwargs) -> None:
    """
    Install Antares Web at the right file locations.
    """
    target_dir = Path(target_dir)
    src_dir = Path(src_dir)

    target_dir = target_dir.expanduser()

    print(f"Starting installation in directory: '{target_dir}'...")
    app = App(source_dir=src_dir, target_dir=target_dir, **kwargs)
    app.run()

    # window = Window()
    # window.mainloop()

    print("Done.")
