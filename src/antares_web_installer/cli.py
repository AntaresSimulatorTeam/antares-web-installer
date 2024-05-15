import os
import click
import psutil

from pathlib import Path
import tkinter as tk
from antares_web_installer.app import App
from antares_web_installer.view import Window

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
    help="where to find the Antares Web package",
)
@click.option(
    "-t",
    "--target-dir",
    default=TARGET_DIR,
    show_default=True,
    type=click.Path(),
    help="where to install your application",
)
def install_cli(src_dir: str, target_dir: str) -> None:
    """
    Install Antares Web at the right file locations.
    """
    target_dir = Path(target_dir)
    src_dir = Path(src_dir)

    target_dir = target_dir.expanduser()

    # check whether the server is running
    server_running_handler()

    print(f"Starting installation in directory: '{target_dir}'...")
    # app = App(src_dir, target_dir)
    # app.run()
    window = Window()
    # print("test screensize: " + str(window.winfo_screenwidth()))
    # window.start()
    window.mainloop()
    print("Done.")


def server_running_handler() -> None:
    """
    Check whether antares service is up.
    In case it is, terminate the process
    """
    for proc in psutil.process_iter(["pid", "name", "username"]):
        if "antares" in proc.name().lower():
            print("Cannot upgrade since the application is running.")

            running_app = psutil.Process(pid=proc.pid)
            running_app.kill()  # ... or terminate ?
            running_app.wait(30)
            assert not running_app.is_running()

            print("The application was successfully stopped.")
            return
