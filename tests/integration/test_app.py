import os
import shutil
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
def downloaded_dir_fixture(antares_web_server_path, tmp_path: Path) -> Path:
    # Prepare the temporary directory to store "download" files
    downloaded_dir = tmp_path.joinpath(DOWNLOAD_FOLDER, "AntaresWeb-MyOS-vX.Y.Z")
    downloaded_dir.mkdir(parents=True)

    # Copy sample data
    sample_dir = SAMPLES_DIR.joinpath(os.name)
    shutil.copytree(sample_dir, downloaded_dir, dirs_exist_ok=True)

    # The sample directory may contain an extra script which must be removed
    downloaded_dir.joinpath("AntaresWeb/AntaresWebServer.py").unlink(missing_ok=True)

    # Patch the `AntaresWeb/AntaresWebServer.exe` file
    shutil.copy2(antares_web_server_path, downloaded_dir.joinpath("AntaresWeb"))
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


class TestApp:
    """
    Integration tests for the app
    """

    def test_run__empty_target(
        self,
        downloaded_dir: Path,
        desktop_dir: Path,
        program_dir: Path,
        monkeypatch: MonkeyPatch,
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
        # Patch the `get_desktop` function according to the current platform
        platform = {"nt": "windows", "posix": "linux", "darwin": "darwin"}[os.name]
        monkeypatch.setattr(f"pyshortcuts.{platform}.get_desktop", lambda: desktop_dir)

        # Run the application
        app = App(source_dir=downloaded_dir, target_dir=program_dir, shortcut=True, launch=True)
        app.run()

        # Check the target directory
        assert program_dir.is_dir()
        assert list(program_dir.iterdir())

        # Check the desktop directory
        assert desktop_dir.is_dir()
        assert list(desktop_dir.iterdir())

        # kill the running server
        for proc in psutil.process_iter():
            if "AntaresWebServer" in proc.name():
                proc.kill()
                proc.wait(1)
                break
