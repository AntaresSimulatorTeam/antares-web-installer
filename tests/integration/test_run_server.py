import socket
import subprocess
import time

import requests  # type: ignore

SPAWN_TIMEOUT = 10
"""Timeout in seconds to wait for the server process to start."""

SERVER_TIMEOUT = 10
"""Timeout in seconds to wait for the server to be ready."""


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


def test_server_health(antares_web_server_paths):
    """
    Test the health endpoint of the Antares web server.
    After retrieving newly built servers, run each, make a
    simple get request and kill it.
    """

    # Set up: run each server
    for server_path in antares_web_server_paths:
        server = subprocess.Popen(
            [str(server_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=False,
        )

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
            if ping("localhost", 8080, timeout=0.1):
                break
            time.sleep(0.1)
        else:
            raise RuntimeError("The server did not start in time.")

        res = requests.get("http://localhost:8080/health", timeout=0.25)
        assert res.status_code == 200, res.json()
        assert res.json() == {"status": "available"}

        # Tear down: kill server and make sure it is terminated
        server.terminate()
        server.wait()
