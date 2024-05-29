import dataclasses
import logging
import os
import subprocess
import textwrap
import webbrowser
from pathlib import Path
from shutil import copy2, copytree, rmtree

import psutil
from pyshortcuts import make_shortcut

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


@dataclasses.dataclass
class App:
    source_dir: Path
    target_dir: Path
    app_name: str = "AntaresWebInstaller"
    os_name: str = os.name
    shortcut: bool = False
    launch: bool = False
    logger = logging.getLogger(__name__)

    def run(self) -> None:
        self.kill_running_server()
        self.install_files()
        if self.shortcut:
            self.create_icons()
        if self.launch:
            self.start_server()

    def kill_running_server(self) -> None:
        """
        Check whether Antares service is up.
        Kill the process if so.
        """
        for proc in psutil.process_iter(["pid", "name"]):
            if "fastapi" in proc.name():
                self.logger.info("Cannot upgrade since the application is running.")

                running_app = psutil.Process(pid=proc.pid)
                running_app.kill()
                running_app.wait(30)

                self.logger.info("The application was successfully stopped.")

    def install_files(self):
        """ """
        # if the target directory already exists and not empty
        if self.target_dir.is_dir() and list(self.target_dir.iterdir()):
            # check app version
            version = self.check_version()
            self.logger.info(f"Current application version : {version}")

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
                            raise InstallError(f"Error : Cannot update the directory {elt_path}")

                        # copy new directory
                        copytree(elt_path, self.target_dir.joinpath(elt_path.name))
                # handle permission errors
                except PermissionError:
                    raise InstallError(f"Error : Cannot write in {self.target_dir}")
                # handle other errors
                except BaseException as e:
                    raise InstallError(f"{e}")

    def check_version(self) -> str:
        """
        Execute command to get the current version of the server.
        """
        script_path = self.target_dir.joinpath("AntaresWeb/AntaresWebServer.py")  # FIXME
        if script_path.exists():
            args = ["python", str(script_path), "--version"]  # FIXME
        else:
            exe_path = self.target_dir.joinpath("AntaresWeb/AntaresWebServer.exe")
            # check user's os
            if self.os_name.lower() == "posix":  # if os is linux, remove ".exe"
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
        # using pyshortcuts
        self.logger.info("Create shortcuts ...")

        # test if it already exists
        make_shortcut(
            script=str(f"{self.target_dir.joinpath('AntaresWeb/AntaresWebServer.py')} run"),
            name="Antares Web Server",
            icon="../../docs/assets/antares-web-installer-icon.ico",
        )  # TODO: edit comment and script

        self.logger.info("Shortcuts was created.")

    def start_server(self):
        """
        Launch the local server as a background task
        """
        args_server = [f"{self.target_dir.joinpath('AntaresWeb/AntaresWebServer.py')}", "run"]
        subprocess.Popen(args=args_server, shell=True)
        webbrowser.open(url="http://localhost:8000/", new=2)
