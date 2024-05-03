import os
import click
from antares_web_installer import DEBUG
from pathlib import Path
from installer import install


# SETTINGS WHEN DEBUGGING
if DEBUG:
    BASE_DIR = Path().resolve().parent.parent

    SRC_DIR = "tests/samples/initial/"
    TARGET_DIR = "tests/samples/results/"
    if os.name.lower() == "posix":
        suffix = "posix/opt/antares-web/"
    else:
        suffix = "nt/Program Files/AntaresWeb/"
    TARGET_DIR += suffix
    SRC_DIR += suffix

# REAL SETTINGS
else:
    if os.name.lower() == "posix":
        TARGET_DIR = "/opt/antares-web/"
    else:
        TARGET_DIR = "C:/Program Files/AntaresWeb/"

    SRC_DIR = ""


@click.group()
def cli():
    pass


@click.command()
@click.option("-t", "--target-dir",
              default=TARGET_DIR,
              show_default=True,
              type=click.Path(),
              help="where to install your application")
def install_cli(target_dir):
    """
    Install Antares Web at the right file locations.
    """
    target_dir = Path(target_dir)
    src_dir = Path(SRC_DIR)

    if DEBUG:
        target_dir = BASE_DIR.joinpath(Path(target_dir))
        src_dir = BASE_DIR.joinpath(Path(src_dir))
    target_dir = target_dir.expanduser()

    # TODO: check whether the server is running
    # in case it is, stop it

    print(f"Starting installation in directory: '{target_dir}'...")

    install(src_dir, target_dir)

    print("Installation complete!")
