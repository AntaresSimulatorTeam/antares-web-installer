import os
import socket
import subprocess
import time
from pathlib import Path

import pytest

from tests.integration.server_mock.builder import build

EXE_NAME = "AntaresWebServer.exe" if os.name == "nt" else "AntaresWebServer"
"""Name of the executable file for the Antares web server."""

SPAWN_TIMEOUT = 1
"""Timeout in seconds to wait for the server process to start."""

SERVER_TIMEOUT = 2
"""Timeout in seconds to wait for the server to be ready."""


@pytest.fixture(name="antares_web_server_path", scope="session", autouse=True)
def antares_web_server_path_fixture(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Fixture used to build the Antares web server application."""
    target_dir = tmp_path_factory.mktemp("antares_web_server", numbered=False)
    return build(target_dir, exe_name=EXE_NAME)


def ping(host: str, port: int, timeout: float = 2) -> bool:
    """
    Checks if a host is reachable by attempting to connect to a specified port.

    Args:
        host: The host to connect to.
        port: The port to connect on.
        timeout: The time in seconds to wait for a connection.

    Returns:
        True if the host is reachable, False otherwise.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((host, port))
    except (socket.timeout, ConnectionError):
        return False
    else:
        return True


@pytest.fixture(name="antares_web_server")
def antares_web_server_fixture(antares_web_server_path: Path) -> subprocess.Popen:
    """Fixture used to provide a running instance of the Antares web server."""
    # Spawn the server process
    server = subprocess.Popen(
        [str(antares_web_server_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        shell=False,
    )

    try:
        # Wait for the subprocess to start
        timeout_time = time.time() + SPAWN_TIMEOUT
        while time.time() < timeout_time:
            if server.poll() is None:
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("The process did not start in time.")

        # Wait for the server to be ready
        timeout_time = time.time() + SERVER_TIMEOUT
        while time.time() < timeout_time:
            if ping("localhost", 8000, timeout=0.1):
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("The server did not start in time.")

        yield server

    finally:
        server.terminate()
        server.wait()
