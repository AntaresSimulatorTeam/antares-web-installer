import os
import pytest

from pathlib import Path
from tests.integration.server_mock.builder import build

EXE_NAME = "AntaresWebServer.exe" if os.name == "nt" else "AntaresWebServer"
"""Name of the executable file for the Antares web server."""


@pytest.fixture(name="antares_web_server_paths", scope="session", autouse=True)
def antares_web_server_paths_fixture(tmp_path_factory: pytest.TempPathFactory) -> [Path]:
    """Fixture used to build both the Antares web server version (2.14.4 and 2.15.2)."""
    target_dir = tmp_path_factory.mktemp("servers", numbered=False)

    apps = []
    for version in ["2.14.4", "2.15.2"]:
        import tests.integration.server_mock.server as server
        server.__dict__["version"] = version
        version_target_dir = target_dir.joinpath("AntaresWeb-"+version)
        apps.append(build(version_target_dir, exe_name=EXE_NAME))

    return apps
