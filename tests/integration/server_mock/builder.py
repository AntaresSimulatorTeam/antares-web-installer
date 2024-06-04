"""
Pyinstaller builder for server mock
"""

import tempfile
from pathlib import Path

from PyInstaller.__main__ import run

HERE = Path(__file__).parent
SERVER_PATH = HERE.joinpath("server.py")


def build(target_dir: Path, exe_name="AntaresWebServer.exe") -> Path:
    """
    Build the server executable using PyInstaller.

    See: https://pyinstaller.org/en/stable/usage.html

    Args:
        target_dir: Target directory where the executable will be created.
        exe_name: Name of the executable file.

    Returns:
        Path to the executable file.
    """
    target_dir.mkdir(exist_ok=True, parents=True)
    with tempfile.TemporaryDirectory(dir=target_dir, prefix="~", suffix=".tmp") as temp_dir:
        args = [
            str(SERVER_PATH),
            "--onefile",
            "--console",
            "--log-level=ERROR",
            f"--distpath={target_dir}",
            f"--workpath={temp_dir}",
            f"--specpath={temp_dir}",
            f"--name={exe_name}",
        ]
        run(args)

    # Add executable permission
    exe_path = target_dir.joinpath(exe_name)
    exe_path.chmod(0o755)

    return exe_path


if __name__ == "__main__":
    build(HERE)
