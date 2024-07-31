import dataclasses
import logging
import os
import re
import subprocess
import textwrap
import time
import webbrowser

from difflib import SequenceMatcher
from pathlib import Path
from shutil import copy2, copytree, SameFileError

import httpx
import psutil

from antares_web_installer.config import update_config
from antares_web_installer.shortcuts import create_shortcut, get_desktop

logger = logging.getLogger(__name__)

# List of files and directories to exclude during installation
COMMON_EXCLUDED_FILES = {"config.prod.yaml", "config.yaml", "examples", "logs", "matrices", "tmp"}
POSIX_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker", "AntaresWebInstaller"}
WINDOWS_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker.exe", "AntaresWebInstaller.exe"}
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
    shortcut: bool = True
    launch: bool = True

    server_path: Path = dataclasses.field(init=False)
    progress: float = dataclasses.field(init=False)
    nb_steps: int = dataclasses.field(init=False)
    completed_step: int = dataclasses.field(init=False)

    def __post_init__(self):
        # Prepare the path to the executable which is located in the target directory
        server_name = SERVER_NAMES[os.name]
        self.server_path = self.target_dir.joinpath("AntaresWeb", server_name)

        # Set all progress variables needed to compute current progress of the installation
        self.nb_steps = 2  # kill, install steps
        if self.shortcut:
            self.nb_steps += 1
        if self.launch:
            self.nb_steps += 2
        self.current_step = 0
        self.progress = 0

    def run(self) -> None:
        self.kill_running_server()
        self.current_step += 1

        self.install_files()
        self.current_step += 1

        if self.shortcut:
            self.create_shortcuts()
            self.current_step += 1

        if self.launch:
            self.start_server()
            self.current_step += 1
            self.open_browser()

    def update_progress(self, progress: float):
        self.progress = (progress / self.nb_steps) + (self.current_step / self.nb_steps) * 100
        logger.info(f"Progression: {self.progress:.2f}")

    def kill_running_server(self) -> None:
        """
        Check whether Antares service is up.
        Kill the process if so.
        """
        processes_list = list(psutil.process_iter(["pid", "name"]))
        processes_list_length = len(processes_list)

        for index, proc in enumerate(processes_list):
            # evaluate matching between query process name and existing process name
            try:
                matching_ratio = SequenceMatcher(None, "antareswebserver", proc.name().lower()).ratio()
            except psutil.NoSuchProcess:
                logger.warning("The process '{}' was stopped before being analyzed. Skipping.".format(proc.name()))
                continue
            if matching_ratio > 0.8:
                logger.info("Running server found. Attempt to stop it ...")
                logger.debug(f"Server process:{proc.name()} -  process id: {proc.pid}")
                running_app = psutil.Process(pid=proc.pid)
                running_app.kill()

                try:
                    running_app.wait(5)
                except psutil.TimeoutExpired as e:
                    raise InstallError(
                        "Impossible to kill the server. Please kill it manually before relaunching the installer."
                    ) from e
                else:
                    logger.info("The application was successfully stopped.")
            self.update_progress((index + 1) * 100 / processes_list_length)
        logger.info("No other processes found.")

    def install_files(self):
        """ """
        logger.info(f"Starting installing files in {self.target_dir}...")

        # if the target directory already exists and isn't empty
        if self.target_dir.is_dir() and list(self.target_dir.iterdir()):
            logger.info("Existing files were found. Proceed checking old version...")
            # check app version
            version = self.check_version()
            logger.info(f"Old application version : {version}.")
            self.update_progress(25)

            # update config file
            logger.info("Update configuration file...")
            config_path = self.target_dir.joinpath("config.yaml")
            update_config(config_path, config_path, version)
            logger.info("Configuration file updated.")
            self.update_progress(50)

            # copy binaries
            logger.info("Update program files...")
            self.copy_files()
            logger.info("Program files updated")
            self.update_progress(75)

            # check new version of the application
            logger.info("Check new application version...")
            version = self.check_version()
            logger.info(f"New application version : {version}.")
            self.update_progress(100)

        else:
            # copy all files from package
            logger.info("No existing files found. Starting file copy...")
            copytree(self.source_dir, self.target_dir, dirs_exist_ok=True)
            logger.info("Files was successfully copied.")
            self.update_progress(100)

    def copy_files(self):
        """
        Copy all files from self.src_dir to self.target_dir
        Override existing files and directories that have the same name
        Raise an InstallError if an error occurs while overriding a directory, if the user hasn't the permission to
        write or if self.target_dir already exists.
        """
        src_dir_content = list(self.source_dir.iterdir())
        src_dir_content_length = len(src_dir_content)

        for index, elt_path in enumerate(src_dir_content):
            if elt_path.name not in EXCLUDED_FILES:
                logger.info(f"Copying '{elt_path}'")
                try:
                    if elt_path.is_file():
                        copy2(elt_path, self.target_dir)
                    else:
                        # copy new directory
                        copytree(elt_path, self.target_dir.joinpath(elt_path.name), dirs_exist_ok=True)
                # handle permission errors
                except PermissionError as e:  # pragma: no cover
                    relpath = elt_path.relative_to(self.source_dir).as_posix()
                    raise InstallError(f"Error: Cannot write '{relpath}' in {self.target_dir}: {e}")
                except SameFileError:
                    # test if current file is the installer
                    pass

                self.update_progress((index + 1) * 100 / src_dir_content_length)

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

        # ensure the version number is in the form 'x.x' or 'x.x.x'
        matched_value = re.match(r"^(\d(.\d)+)+", version)

        if not matched_value:
            raise InstallError("No version found.")

        version = matched_value.group()

        logger.info("Version found.")
        return version

    def create_shortcuts(self):
        """
        Create a local server icon and a browser icon on desktop and
        """
        # prepare a shortcut into the desktop directory
        logger.info("Generating server shortcut on desktop...")
        shortcut_name = SHORTCUT_NAMES[os.name]
        shortcut_path = Path(get_desktop()).joinpath(shortcut_name)

        # if the shortcut already exists, remove it
        shortcut_path.unlink(missing_ok=True)
        self.update_progress(50)

        # shortcut generation
        logger.info(
            f"Shortcut will be created in {shortcut_path}, "
            f"linked to '{self.server_path}' "
            f"and located in '{self.target_dir}' directory."
        )
        create_shortcut(
            shortcut_path,
            exe_path=self.server_path,
            working_dir=self.target_dir,
            description="Launch Antares Web Server in background",
        )

        logger.info("Server shortcut was successfully created.")
        self.update_progress(100)

    def start_server(self):
        """
        Launch the local server as a background task
        """
        logger.info("Attempt to start the newly installed server...")
        args = [str(self.server_path)]
        server_process = subprocess.Popen(
            args=args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
            cwd=self.target_dir,
        )
        self.update_progress(50)

        if not server_process.poll():
            logger.info("Server is starting up ...")
        else:
            logger.info(f"The server unexpectedly stopped running. (code {server_process.returncode})")

        nb_attempts = 0
        max_attempts = 5

        while nb_attempts < max_attempts:
            attempt_info = f"Attempt #{nb_attempts}: "
            try:
                res = httpx.get("http://localhost:8080/", timeout=1)
            except httpx.ConnectError:
                logger.info(attempt_info + "The server is not accepting request yet. Retry ...")
            except httpx.ConnectTimeout:
                logger.info(attempt_info + "The server cannot retrieve a response yet. Retry ...")
            else:
                if res.status_code:
                    logger.info("Server is now available.")
                    self.update_progress(100)
                    break
            finally:
                nb_attempts += 1
                if nb_attempts == max_attempts:
                    raise InstallError(f"Impossible to launch Antares Web Server after {nb_attempts} attempts.")
                time.sleep(5)

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
            logger.info("Browser was successfully opened.")
        self.update_progress(100)
