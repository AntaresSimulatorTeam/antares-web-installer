import dataclasses
import os
import subprocess
import sys
import textwrap
from shutil import copy2, rmtree, copytree

import psutil
import tkinter as tk

from tkinter import ttk
from pathlib import Path

from antares_web_installer.config import update_config

# List of files and directories to exclude during installation
COMMON_EXCLUDED_FILES = {"config.prod.yaml", "config.yaml", "examples", "logs", "matrices", "tmp"}
POSIX_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker"}
WINDOWS_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker.exe"}
EXCLUDED_FILES = POSIX_EXCLUDED_FILES if os.name == "posix" else WINDOWS_EXCLUDED_FILES


class InstallError(Exception):
    """
    Exception that handles installation error
    """

    pass


@dataclasses.dataclass
class App:
    source_dir: Path
    target_dir: Path
    app_name: str = "AntaresWebInstaller"
    os_name: str = os.name
    window_width: int = 640
    window_height: int = 480
    side_img: tk.PhotoImage = None

    # def __post_init__(self):
    #     self.source_dir = Path(self.source_dir)
    #     self.target_dir = Path(self.target_dir)

    def run(self) -> None:
        self.server_running_handler()
        self.install_files()
        # self.create_icons()
        # self.start_server()
        # self.open_web_browser()


    def server_running_handler(self) -> None:
        """
        Check whether antares service is up.
        In this case, terminate the process
        """
        for proc in psutil.process_iter(["pid", "name"]):
            if self.app_name in proc.name():
                print("Cannot upgrade since the application is running.")

                running_app = psutil.Process(pid=proc.pid)
                running_app.kill()  # ... or terminate ?
                running_app.wait(30)
                assert not running_app.is_running()

                print("The application was successfully stopped.")
                return

    def install_files(self):
        """
        """
        # if the target directory already exists and not empty
        if self.target_dir.is_dir() and list(self.target_dir.iterdir()):
            # check app version
            version = self.check_version()
            print(f"Current application version : {version}")

            # update config file
            config_path = self.target_dir.joinpath("config.yaml")
            update_config(config_path, config_path, version)

            # copy binaries
            self.copy_files()

        else:
            # copy all files from package
            copytree(self.source_dir, self.target_dir)

    def copy_files(self):
        """
        Copy all files from self.src_dir to self.target_dir
        Override existing files and directories that have the same name
        Raise an InstallError if an error occurs while overriding a directory, if the user hasn't the permission to write or
        if self.target_dir already exists.
        """
        for elt_path in self.source_dir.iterdir():
            if elt_path.name not in EXCLUDED_FILES:
                # verbose action ?
                try:
                    if elt_path.is_file():
                        copy2(elt_path, self.target_dir)
                    else:
                        # copytree() cannot natively override directory
                        # the target must be deleted first
                        rmtree(self.target_dir.joinpath(elt_path.name))

                        # check if the old directory is completely erased
                        if self.target_dir.joinpath(elt_path.name).exists():
                            raise InstallError(f"Erreur : Impossible de mettre à jour le répertoire {elt_path}")

                        # copy new directory
                        copytree(elt_path, self.target_dir.joinpath(elt_path.name))
                # handle permission errors
                except PermissionError:
                    raise InstallError(f"Erreur : Impossible d'écrire dans {self.target_dir}")
                # handle other errors
                except BaseException as e:
                    raise InstallError(f"{e}")

    def check_version(self) -> str:
        """
        Execute command to get the current version of the server.
        """
        script_path = self.target_dir.joinpath("AntaresWeb/AntaresWebServer.py")
        if script_path.exists():
            args = [sys.executable, str(script_path), "--version"]
        else:
            exe_path = self.target_dir.joinpath("AntaresWeb/AntaresWebServer.exe")
            # check user's os
            if os.name.lower() == "posix":  # if os is linux, remove ".exe"
                exe_path = exe_path.with_suffix("")
            args = [str(exe_path), "--version"]

        try:
            version = subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()
        except FileNotFoundError as e:
            raise InstallError(f"Can't check version: {e}") from e
        except subprocess.CalledProcessError as e:
            reason = textwrap.indent(e.stderr, "  | ", predicate=lambda line: True)
            raise InstallError(f"Can't check version:\n{reason}") from e

        return version

    def create_icons(self):
        """
        Create a local server icon and a browser icon on desktop and
        """
        pass

    def start_server(self):
        """
        Launch the local server as a background task
        """
        pass

    def open_web_browser(self):
        """
        Open Antares Web on the default user browser
        """
        pass
