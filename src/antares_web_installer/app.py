import dataclasses
import logging
import os
import subprocess
import textwrap
import time
import webbrowser
from pathlib import Path
from shutil import copy2, copytree

import psutil

from antares_web_installer.config import update_config
from antares_web_installer.shortcuts import create_shortcut, get_desktop

logger = logging.getLogger(__name__)

# List of files and directories to exclude during installation
COMMON_EXCLUDED_FILES = {"config.prod.yaml", "config.yaml", "examples", "logs", "matrices", "tmp"}
POSIX_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker"}
WINDOWS_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker.exe"}
EXCLUDED_FILES = POSIX_EXCLUDED_FILES if os.name == "posix" else WINDOWS_EXCLUDED_FILES

SERVER_NAMES = {"posix": "AntaresWebServer", "nt": "AntaresWebServer.exe"}
SHORTCUT_NAMES = {"posix": "AntaresWebServer.desktop", "nt": "AntaresWebServer.lnk"}


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
    browser: bool = False

    server_path: Path = dataclasses.field(init=False)

    def __post_init__(self):
        # Prepare the path to the executable which is located in the target directory
        server_name = SERVER_NAMES[self.os_name]
        self.server_path = self.target_dir.joinpath("AntaresWeb", server_name)

    def run(self) -> None:
        self.kill_running_server()
        self.install_files()
        if self.shortcut:
            self.create_shortcuts()
        if self.launch:
            self.start_server()
        if self.browser:
            self.open_browser()

    def kill_running_server(self) -> None:
        """
        Check whether Antares service is up.
        Kill the process if so.
        """
        server_name = SERVER_NAMES[self.os_name]
        for proc in psutil.process_iter(["pid", "name"]):
            if server_name.lower() in proc.name().lower():
                logger.info("Running server found. We will attempt to stop it.")

                running_app = psutil.Process(pid=proc.pid)
                running_app.kill()
                running_app.wait(15)

                logger.info("The application was successfully stopped.")

        logger.info("No other processes found.")

    def install_files(self):
        """ """
        # if the target directory already exists and isn't empty
        if self.target_dir.is_dir() and list(self.target_dir.iterdir()):
            # check app version
            version = self.check_version()
            logger.info(f"Old application version : {version}.")

            # update config file
            config_path = self.target_dir.joinpath("config.yaml")
            update_config(config_path, config_path, version)
            logger.info(f"New application version : {version}.")

            # copy binaries
            self.copy_files()

        else:
            # copy all files from package
            copytree(self.source_dir, self.target_dir)

    def copy_files(self):
        """
        Copy all files from self.src_dir to self.target_dir
        Override existing files and directories that have the same name
        Raise an InstallError if an error occurs while overriding a directory, if the user hasn't the permission to
        write or if self.target_dir already exists.
        """
        for elt_path in self.source_dir.iterdir():
            if elt_path.name not in EXCLUDED_FILES:
                try:
                    if elt_path.is_file():
                        logger.info(f"'{elt_path}' file found and isn't an excluded file.")
                        copy2(elt_path, self.target_dir)
                    else:
                        # copy new directory
                        logger.info(f"'{elt_path}' directory found and isn't an excluded directory.")
                        copytree(elt_path, self.target_dir.joinpath(elt_path.name), dirs_exist_ok=True)

                # handle permission errors
                except PermissionError as e:
                    raise InstallError(f"Error : Cannot write in {self.target_dir}:") from e

    def check_version(self) -> str:
        """
        Execute command to get the current version of the server.
        """
        # check user's os
        args = [str(self.server_path), "--version"]

        try:
            logger.info("Attempt to get version of Antares server...")
            version = subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()
        except FileNotFoundError as e:
            raise InstallError(f"Can't check version: {e}") from e
        except subprocess.CalledProcessError as e:
            reason = textwrap.indent(e.stderr, "  | ", predicate=lambda line: True)
            raise InstallError(f"Can't check version:\n{reason}") from e

        logger.info("Version found.")
        return version

    def create_shortcuts(self):
        """
        Create a local server icon and a browser icon on desktop and
        """
        # using pyshortcuts
        logger.info("Generating server shortcut...")

        # prepare a shortcut into the desktop directory
        shortcut_name = SHORTCUT_NAMES[self.os_name]
        shortcut_path = Path(get_desktop()).joinpath(shortcut_name)

        # if the shortcut already exists, remove it
        shortcut_path.unlink(missing_ok=True)

        # create a new shortcut
        create_shortcut(
            shortcut_path,
            exe_path=self.server_path,
            working_dir=self.target_dir,
            description="Launch Antares Web Server in background",
        )

        # # if user's os is linux
        # if self.os_name.lower() == "posix":
        #     logger.info("Unix os detected.")
        #
        #     # 1. create a .desktop
        #     desktop_path = os.popen("xdg-user-dir DESKTOP").read().rstrip("\n")
        #     shortcut_name = "AntaresWebServer.desktop"
        #     shortcut_path = desktop_path + "/" + shortcut_name
        #     os.popen(f"touch {shortcut_path}")
        #
        #     # 2. write the default desktop entry
        #     with resources.path(
        #         "antares_web_installer.assets.img", "antares-web-installer-logo.png"
        #     ) as icon_path:  # deprecated since 3.11 version
        #         with open(shortcut_path, mode="w") as file:
        #             content = (
        #                 f"[Desktop Entry]\n"
        #                 f"Version=1.0\n"
        #                 f"Type=Application\n"
        #                 f"Terminal=true\n"
        #                 f"Exec={str(self.target_file.resolve().expanduser())}\n"
        #                 f"Name=Antares Web Server\n"
        #                 f"Comment=Launch Antares web server\n"
        #                 f"Icon={str(icon_path.resolve().expanduser())}"
        #             )
        #
        #             file.write(content)
        #
        #     # 4. activate allow launching option
        #     os.popen(f"chmod u+x {shortcut_path}")
        #     logger.info("Execution rights were updated")
        #
        #     os.popen(f"gio set {shortcut_path} metadata::trusted true")
        #     logger.info("Shortcut is now allowed to launch the server.")
        #
        #     # 5. Option add to application list
        #     # os.popen(f"")
        #
        #     # 6. Option : add to path
        #     # alias_command = f"alias AntaresWebServer=$PATH:{self.target_dir}\nalias antareswebserver=AntaresWebServer\n"
        #     # os.popen(f"echo  '{alias_command}' >> {shortcut_path}")
        #
        # # otherwise, consider user's os is windows
        # else:
        #     _win32_shell.create_shortcut(self.target_dir, self.target_file)

        # test if it already exists
        logger.info("Server shortcut was created.")

    def start_server(self):
        """
        Launch the local server as a background task
        """
        args = [str(self.server_path)]
        server_process = subprocess.Popen(args=args, shell=True, start_new_session=True)
        time.sleep(1.5)  # wait for the server to complete startup
        if server_process.poll() is None:
            logger.info("Server was started successfully.")

    def open_browser(self):
        """
        Open server URL in default user's browser
        """
        url = "http://localhost:8080/"
        try:
            webbrowser.open(url=url, new=2)
        except webbrowser.Error as e:
            raise InstallError(f"Could not open browser at '{url}': {e}") from e
        else:
            logger.info(f"Browser was successfully opened at '{url}'.")
