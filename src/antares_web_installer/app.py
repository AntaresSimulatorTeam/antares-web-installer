import dataclasses
import os
import re
import subprocess
import textwrap
import time
from difflib import SequenceMatcher
from pathlib import Path
from shutil import copy2, copytree
from typing import List

import requests

if os.name == "nt":
    from pythoncom import com_error

import psutil

from antares_web_installer import logger
from antares_web_installer.config import update_config
from antares_web_installer.shortcuts import create_shortcut, get_desktop

# List of files and directories to exclude during installation
COMMON_EXCLUDED_RESOURCES = {
    Path("config.yaml"),
    Path("archives"),
    Path("internal_studies"),
    Path("studies"),
    Path("logs"),
    Path("matrices"),
    Path("tmp"),
    Path("local_workspace"),
}

POSIX_EXCLUDED_FILES = COMMON_EXCLUDED_RESOURCES | {Path("AntaresWebInstallerCLI")}
WINDOWS_EXCLUDED_FILES = COMMON_EXCLUDED_RESOURCES | {Path("AntaresWebInstaller.exe")}
EXCLUDED_ROOT_RESOURCES = POSIX_EXCLUDED_FILES if os.name == "posix" else WINDOWS_EXCLUDED_FILES


SERVER_NAMES = {"posix": "AntaresWebServer", "nt": "AntaresWebServer.exe"}
SHORTCUT_NAMES = {"posix": "AntaresWebServer.desktop", "nt": "AntaresWebServer.lnk"}

SERVER_ADDRESS = "http://127.0.0.1:8080"
HEALTHCHECK_ADDRESS = f"{SERVER_ADDRESS}/api/health"

MAX_SERVER_START_TIME = 120


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
    version: str = dataclasses.field(init=False)

    def __post_init__(self):
        # Prepare the path to the executable which is located in the target directory
        server_name = SERVER_NAMES[os.name]
        self.server_path = self.target_dir / "AntaresWeb" / server_name

        # Set all progress variables needed to compute current progress of the installation
        self.nb_steps = 2  # kill, install steps
        if self.shortcut:
            self.nb_steps += 1
        if self.launch:
            self.nb_steps += 1
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

    def update_progress(self, progress: float):
        self.progress = (progress / self.nb_steps) + (self.current_step / self.nb_steps) * 100
        logger.info(f"Progression: {self.progress:.2f}")

    def kill_running_server(self) -> None:
        """
        Check whether Antares service is up.
        Kill the process if so.
        """
        server_processes = self._get_server_processes()
        if len(server_processes) > 0:
            logger.info("Attempt to stop running Antares server ...")
            for p in server_processes:
                try:
                    p.kill()
                except psutil.NoSuchProcess:
                    logger.debug(f"The process '{p.pid}' was stopped before being killed.")
                    continue
            gone, alive = psutil.wait_procs(server_processes, timeout=5)
            alive_count = len(alive)
            if alive_count > 0:
                raise InstallError(
                    "Could not to stop Antares server. Please stop it before launching again the installation."
                )
            else:
                logger.info("Antares server successfully stopped...")
        else:
            logger.info("No running server found, resuming installation.")
        self.update_progress(100)

    def _get_server_processes(self) -> List[psutil.Process]:
        res = []
        for process in psutil.process_iter(["pid", "name"]):
            try:
                # evaluate matching between query process name and existing process name
                matching_ratio = SequenceMatcher(None, "antareswebserver", process.name().lower()).ratio()
            except FileNotFoundError:
                logger.warning("The process '{}' does not exist anymore. Skipping its analysis".format(process.name()))
                continue
            except psutil.NoSuchProcess:
                logger.warning("The process '{}' was stopped before being analyzed. Skipping.".format(process.name()))
                continue
            if matching_ratio > 0.8:
                res.append(process)
                logger.debug(f"Running server found: {process.name()} -  process id: {process.pid}")
        return res

    def install_files(self):
        """ """
        logger.info(f"Starting installing files in {self.target_dir}...")

        # if the target directory already exists and isn't empty
        if self.target_dir.is_dir() and list(self.target_dir.iterdir()):
            logger.info("Existing files were found. Proceed checking old version...")
            # check app version
            old_version = self.check_version()
            logger.info(f"Old application version : {old_version}.")
            version_info = tuple(map(int, old_version.split(".")))
            if version_info < (2, 18):
                raise InstallError(
                    f"Trying to update from version {old_version}: updating from version older than 2.18 is not supported, please select a new installation directory."
                )
            self.update_progress(25)

            # update config file
            logger.info("Update configuration file...")
            src_config_path = self.source_dir.joinpath("config.yaml")
            target_config_path = self.target_dir.joinpath("config.yaml")
            update_config(src_config_path, target_config_path, old_version)
            logger.info("Configuration file updated.")
            self.update_progress(50)

            # copy binaries
            logger.info("Update program files...")
            self.copy_files()
            logger.info("Program files updated")
            self.update_progress(75)

            # check new version of the application
            logger.info("Check new application version...")
            self.version = self.check_version()
            logger.info(f"New application version : {self.version}.")
            self.update_progress(100)

        else:
            # copy all files from package
            logger.info("No existing files found. Starting file copy...")
            copytree(self.source_dir, self.target_dir, dirs_exist_ok=True)
            logger.info("Files was successfully copied.")
            self.version = self.check_version()
            self.update_progress(100)

    def copy_files(self):
        """
        Copy all files from self.src_dir to self.target_dir
        Override existing files and directories that have the same name
        Raise an InstallError if an error occurs while overriding a directory, if the user hasn't the permission to
        write or if self.target_dir already exists.
        """
        src_dir_content = list(self.source_dir.iterdir())
        dirs_to_copy = []
        for root_dir in src_dir_content:
            if root_dir.relative_to(self.source_dir) not in EXCLUDED_ROOT_RESOURCES:
                dirs_to_copy.append(root_dir)
        src_dir_content_length = len(dirs_to_copy)

        initial_value = self.progress

        for index, elt_path in enumerate(dirs_to_copy):
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

            self.update_progress(initial_value + (index + 1) * 100 / src_dir_content_length)
        logger.info("File copy completed.")

    def check_version(self) -> str:
        """
        Execute command to get the current version of the server.
        """
        # check user's os
        args = [str(self.server_path), "--version"]

        try:
            logger.info("Attempt to get version of Antares server...")
            version = subprocess.check_output(args, text=True, stderr=subprocess.PIPE, timeout=30).strip()
        except FileNotFoundError as e:
            raise InstallError(f"Can't check version: {e}") from e
        except subprocess.CalledProcessError as e:
            reason = textwrap.indent(e.stderr, "  | ", predicate=lambda line: True)
            raise InstallError(f"Can't check version:\n{reason}") from e
        except subprocess.TimeoutExpired as e:
            raise InstallError(f"Impossible to check previous version: {e}") from e

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
        desktop_path = Path(get_desktop())

        logger.info("Generating server shortcut on desktop...")
        name, ext = SHORTCUT_NAMES[os.name].split(".")
        new_shortcut_name = f"{name}-{self.version}.{ext}"
        shortcut_path = desktop_path.joinpath(new_shortcut_name)

        # if the shortcut already exists, remove it
        shortcut_path.unlink(missing_ok=True)
        self.update_progress(50)

        # shortcut generation
        logger.info(
            f"Shortcut {new_shortcut_name} will be created in {shortcut_path}, "
            f"linked to '{self.server_path}' "
            f"and located in '{self.target_dir}' directory."
        )

        try:
            create_shortcut(
                shortcut_path,
                exe_path=self.server_path,
                working_dir=self.target_dir,
                description="Launch Antares Web Server in background",
            )
        except com_error as e:
            raise InstallError(f"Impossible to create a new shortcut: {e}\nSkipping shortcut creation") from e
        else:
            assert shortcut_path in list(desktop_path.iterdir())
            logger.info(f"Server shortcut {shortcut_path} was successfully created.")
        self.update_progress(100)

    def start_server(self):
        """
        Launch the local server as a background task
        """
        logger.info(f"Attempt to start the newly installed server located in '{self.target_dir}'...")
        logger.debug(f"User permissions: {os.path.exists(self.server_path) and os.access(self.server_path, os.X_OK)}")

        args = [self.server_path]
        server_process = subprocess.Popen(
            args=args,
            cwd=self.target_dir,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True,
        )
        self.update_progress(50)

        start_time = time.time()
        nb_attempts = 1
        while time.time() - start_time < MAX_SERVER_START_TIME:
            logger.info(f"Waiting for server start (attempt #{nb_attempts})...")
            if server_process.poll() is not None:
                raise InstallError("Server failed to start, please check server logs.")
            try:
                res = requests.get(HEALTHCHECK_ADDRESS)
                if res.status_code == 200:
                    logger.info("The server is now running.")
                    break
                else:
                    logger.debug(f"Got HTTP status code {res.status_code} while requesting {HEALTHCHECK_ADDRESS}")
                    logger.debug(f"Content: {res.text}")
            except requests.RequestException as req_err:
                logger.debug(f"Error while requesting {HEALTHCHECK_ADDRESS}: {req_err}", exc_info=req_err)
            time.sleep(1)
            nb_attempts += 1
        else:
            raise InstallError("Server didn't start in time, please check server logs.")
        self.update_progress(100)
