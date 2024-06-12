import typing as t
import importlib
import os
import sys


_PKG = "antares_web_installer.shortcuts"

# https://stackoverflow.com/a/13874620/1513933
_shell_module = importlib.import_module(f"{_PKG}._{sys.platform}_shell")


def get_homedir() -> str:
    """
    Return the path to the user's home directory.
    """
    return _shell_module.get_homedir()


def get_desktop() -> str:
    """
    Return the path to the user's desktop directory.
    """
    return _shell_module.get_desktop()


def get_start_menu() -> str:
    """
    Return the path to the user's start menu directory.
    """
    return _shell_module.get_start_menu()


def create_shortcut(
    target: t.Union[str, os.PathLike],
    exe_path: t.Union[str, os.PathLike],
    *,
    arguments: t.Union[str, t.Sequence[str]] = "",
    working_dir: t.Union[str, os.PathLike] = "",
    icon_path: t.Union[str, os.PathLike] = "",
    description: str = "",
) -> None:
    """
    Creates a shortcut to an executable.

    Args:
        target: The path to the shortcut file to be created.
        exe_path: The path to the executable that the shortcut should launch.
        arguments: The arguments to be passed to the executable.
        working_dir: The working directory for the executable.
        icon_path: The path to the icon for the shortcut.
        description: The description of the shortcut.
    """
    return _shell_module.create_shortcut(
        target,
        exe_path,
        arguments=arguments,
        working_dir=working_dir,
        icon_path=icon_path,
        description=description,
    )


if __name__ == "__main__":
    print(f"{get_homedir()=}")
    print(f"{get_desktop()=}")
    print(f"{get_start_menu()=}")
