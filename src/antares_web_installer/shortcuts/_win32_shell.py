"""
TODO : script file description, comments, logs,
"""

import os
import typing as t
import pywintypes

import win32com.client
from win32com.shell import shell, shellcon

_WSHELL = win32com.client.Dispatch("Wscript.Shell")

# Windows Special Folders
# see: https://docs.microsoft.com/en-us/windows/win32/shell/csidl


class ShortcutCreationError(Exception):
    pass


def get_homedir() -> str:
    """Return home directory:
    note that we return CSIDL_PROFILE, not
    CSIDL_APPDATA, CSIDL_LOCAL_APPDATA,  or CSIDL_COMMON_APPDATA
    """
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PROFILE, None, 0)


def get_desktop() -> str:
    """Return user Desktop folder"""
    return shell.SHGetFolderPath(0, shellcon.CSIDL_DESKTOP, None, 0)


def get_start_menu() -> str:
    """Return user Start Menu Programs folder
    note that we return CSIDL_PROGRAMS not CSIDL_COMMON_PROGRAMS
    """
    return shell.SHGetFolderPath(0, shellcon.CSIDL_PROGRAMS, None, 0)


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
    else:
        arguments = [arg for arg in arguments]

    try:
        wscript = _WSHELL.CreateShortCut(str(target))
        wscript.TargetPath = str(exe_path)
        wscript.Arguments = " ".join(arguments)
        wscript.WorkingDirectory = str(working_dir)
        wscript.WindowStyle = 0
        wscript.Description = str(description) if description else "$null"
        wscript.IconLocation = str(exe_path) if exe_path else "$null"
        wscript.save()
    except TypeError as e:
        raise ShortcutCreationError(f"Unsupported field type for shortcut configuration: {e}") from e
    except AttributeError as e:
        raise ShortcutCreationError(f"Unknown attribute: {e}") from e
    except pywintypes.com_error as e:
        raise ShortcutCreationError(f"An error occurred while saving shortcut: {e}") from e
