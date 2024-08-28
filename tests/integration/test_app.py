import os
import shutil
from difflib import SequenceMatcher
from pathlib import Path

import psutil
import pytest
from _pytest.monkeypatch import MonkeyPatch

from antares_web_installer.app import App
from tests.samples import SAMPLES_DIR

DOWNLOAD_FOLDER = "Download"
DESKTOP_FOLDER = "Desktop"
PROGRAM_FOLDER = "Program Files"


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
    # Patch the `get_desktop` function according to the current platform
    platform = {"nt": "_win32_shell", "posix": "_linux_shell"}[os.name]
    monkeypatch.setattr(f"antares_web_installer.shortcuts.{platform}.get_desktop", lambda: desktop_dir)
    yield
    # kill the running servers
    for proc in psutil.process_iter():
        matching_ratio = SequenceMatcher(None, "antareswebserver", proc.name().lower()).ratio()
        if matching_ratio > 0.8:
            proc.kill()
            proc.wait(1)
            break


class TestApp:
    """
    Integration tests for the app
    """
    def test_run__empty_target(
        self,
        downloaded_dir: Path,
        program_dir: Path,
        settings: None
    ) -> None:
        """
        The goal of this test is to verify the behavior of the application when:
        - The Antares server is not running
        - The target directory is empty

        The test must verify that:
        - Files are correctly copied to the target directory
        - Shortcuts are correctly created on the desktop
        - The server is correctly started
        """
        # For each application versions, check if everything is working
        for application_dir in downloaded_dir.iterdir():
            # Run the application
            app = App(source_dir=application_dir, target_dir=program_dir, shortcut=True, launch=True)
            app.run()

    def test_shortcut__created(
            self,
            downloaded_dir: Path,
            program_dir: Path,
            desktop_dir: Path,
            settings: None
    ):
        for application_dir in downloaded_dir.iterdir():
            # Run the application
            app = App(source_dir=application_dir, target_dir=program_dir, shortcut=True, launch=True)
            app.run()

            desktop_files = [file_name.name for file_name in list(desktop_dir.iterdir())]

            if os.name != "nt":
                assert "AntaresWebServer.desktop" in desktop_files
            else:
                assert "Antares Web Server.lnk" in desktop_files

    def test_shortcut__not_created(self):
        """
        Test if a shortcut was created on the desktop
        @param downloaded_dir:
        @param desktop_dir:
        @param program_dir:
        @return:
        """
        pass


