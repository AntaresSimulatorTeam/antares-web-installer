"""
This module allows to create shortcuts on Windows using the `win32com.shell.shell` module.

It must present the same interface as the `antares_web_installer.shortcuts` module:

- `get_homedir()`: Return the path to the user's home directory.
- `get_desktop()`: Return the path to the user's desktop directory.
- `get_start_menu()`: Return the path to the user's start menu directory.
- `create_shortcut()`: Creates a shortcut to an executable.
"""

import os
import typing as t
from contextlib import contextmanager

import pythoncom
import win32com.client
from win32com.shell import shell, shellcon

# Windows Special Folders
# see: https://docs.microsoft.com/en-us/windows/win32/shell/csidl


def get_homedir() -> str:
    """Return home directory:
    note that we return CSIDL_PROFILE, not
    CSIDL_APPDATA, CSIDL_LOCAL_APPDATA,  or CSIDL_COMMON_APPDATA
    """
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None, 0)  # type: ignore


def get_desktop() -> str:
    """Return user Desktop folder"""
    return shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)  # type: ignore


def get_start_menu() -> str:
    """Return user Start Menu Programs folder
    note that we return CSIDL_PROGRAMS not CSIDL_COMMON_PROGRAMS
    """
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0)  # type: ignore


@contextmanager
def initialize_com():
    try:
        pythoncom.CoInitialize()
        yield
    finally:
        pythoncom.CoUninitialize()


def create_shortcut(
    target: t.Union[str, os.PathLike],
    exe_path: t.Union[str, os.PathLike],
    *,
    arguments: t.Union[str, t.Sequence[str]] = "",
    working_dir: t.Union[str, os.PathLike] = "",
    icon_path: t.Union[str, os.PathLike] = "",
    description: str = "",
) -> None:
    working_dir = working_dir or get_homedir()

    if isinstance(arguments, str):
        arguments = [arguments] if arguments else []

    with initialize_com():
        _WSHELL = win32com.client.Dispatch("Wscript.Shell")
        wscript = _WSHELL.CreateShortCut(str(target))
        wscript.TargetPath = str(exe_path)
        wscript.Arguments = " ".join(arguments)
        wscript.WorkingDirectory = str(working_dir)
        wscript.WindowStyle = 0
        if description:
            wscript.Description = description
        if icon_path:
            wscript.IconLocation = str(icon_path)
        wscript.save()
