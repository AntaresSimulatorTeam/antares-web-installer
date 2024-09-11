import os
import shutil
import time

import psutil
import pytest
import re

from difflib import SequenceMatcher
from pathlib import Path
from typing import Any

from _pytest.monkeypatch import MonkeyPatch

from antares_web_installer.app import App, InstallError
from tests.samples import SAMPLES_DIR

DOWNLOAD_FOLDER = "Download"
DESKTOP_FOLDER = "Desktop"
PROGRAM_FOLDER = "ProgramFiles"


@pytest.fixture(name="downloaded_dir")
def downloaded_dir_fixture(antares_web_server_paths, tmp_path: Path) -> Path:
    # Prepare the temporary directory to store "download" files
    downloaded_dir = tmp_path.joinpath(DOWNLOAD_FOLDER)
    downloaded_dir.mkdir(parents=True)

    # Copy sample data
    sample_dir = SAMPLES_DIR.joinpath(os.name)
    shutil.copytree(sample_dir, downloaded_dir, dirs_exist_ok=True)

    for server_path in antares_web_server_paths:
        target_dir = downloaded_dir.joinpath(server_path.parent.name)
        shutil.copy2(server_path, target_dir.joinpath("AntaresWeb"))
        target_dir.joinpath("AntaresWeb/cli.py").unlink(missing_ok=True)
        target_dir.joinpath("AntaresWeb/server.py").unlink(missing_ok=True)
    return downloaded_dir


@pytest.fixture(name="desktop_dir")
def desktop_dir_fixture(tmp_path: Path) -> Path:
    desktop_dir = tmp_path.joinpath(DESKTOP_FOLDER)
    desktop_dir.mkdir(parents=True)
    return desktop_dir


@pytest.fixture(name="program_dir")
def program_dir_fixture(tmp_path: Path) -> Path:
    program_dir = tmp_path.joinpath(PROGRAM_FOLDER)
    program_dir.mkdir(parents=True)
    return program_dir


@pytest.fixture()
def settings(desktop_dir: Path, monkeypatch: MonkeyPatch):
    print("Set up data ...")
    # Patch the `get_desktop` function according to the current platform
    platform = {"nt": "_win32_shell", "posix": "_linux_shell"}[os.name]
    monkeypatch.setattr(f"antares_web_installer.shortcuts.{platform}.get_desktop", lambda: desktop_dir)
    print("Data was set up successfully")
    yield
    # kill the running servers
    print("Starting killing servers.")
    for proc in psutil.process_iter():
        try:
            matching_ratio = SequenceMatcher(None, "antareswebserver", proc.name().lower()).ratio()
        except psutil.NoSuchProcess:
            continue
        if matching_ratio > 0.8:
            proc.kill()
            proc.wait(1)
            break
    print("Severs were successfully killed.")


class TestApp:
    """
    Integration tests for the app
    """

    @staticmethod
    def count_shortcut_file(dir_path: Path) -> int:
        match = 0
        for file in list(dir_path.iterdir()):
            if os.name == "nt":
                pattern = re.compile(r"AntaresWebServer-([0-9]*\.){3}lnk")
                if pattern.fullmatch(file.name):
                    match += 1
            else:
                pattern = re.compile(r"AntaresWebServer-([0-9]*\.){3}desktop")
                if pattern.fullmatch(file.name):
                    match += 1
        return match

    def kill_running_server(self):
        pass

    def test_run__empty_target(self, downloaded_dir: Path, program_dir: Path, settings: Any) -> None:
        """
        The goal of this test is to verify the behavior of the application when:
        - The Antares server is not running
        - The target directory is empty

        The test must verify that:
        - Files are correctly copied to the target directory
        - The server is correctly started
        """
        for source_dir in downloaded_dir.iterdir():
            # Run the application
            # Make sure each application is installed in new directory
            custom_dir = program_dir.joinpath(source_dir.name)
            app = App(
                source_dir=source_dir,
                target_dir=custom_dir,
                shortcut=False,
                launch=True
            )
            try:
                app.run()
            except InstallError:
                print("Server execution problem")
                raise

            # check if application was successfully installed in the target dir (program_dir)
            assert custom_dir.is_dir()
            assert custom_dir.iterdir()

            # check if all files are identical in both source_dir (application_dir) and target_dir (program_dir)
            program_dir_content = list(custom_dir.iterdir())
            source_dir_content = list(source_dir.iterdir())
            assert len(source_dir_content) == len(program_dir_content)
            for index, file in enumerate(source_dir.iterdir()):
                assert file.name == program_dir_content[index].name

            # give some time for the server to shut down
            time.sleep(2)

    def test_shortcut__created(self, downloaded_dir: Path, program_dir: Path, desktop_dir: Path, settings: Any):
        for application_dir in downloaded_dir.iterdir():
            # Run the application
            # Deactivate launch option in order to improve tests speed
            app = App(source_dir=application_dir, target_dir=program_dir, shortcut=True, launch=False)
            app.run()
            match = self.count_shortcut_file(desktop_dir)
            assert match == 1

    def test_shortcut__not_created(self, downloaded_dir: Path, program_dir: Path, desktop_dir: Path, settings: Any):
        """
        Test if a shortcut was created on the desktop
        @param downloaded_dir:
        @param desktop_dir:
        @param program_dir:
        @return:
        """
        for application_dir in downloaded_dir.iterdir():
            # Run the application
            # Deactivate launch option in order to improve tests speed
            app = App(source_dir=application_dir, target_dir=program_dir, shortcut=False, launch=False)
            app.run()
            match = self.count_shortcut_file(desktop_dir)
            assert match == 0
