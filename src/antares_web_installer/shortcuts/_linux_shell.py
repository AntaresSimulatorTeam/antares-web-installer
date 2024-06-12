"""
TODO: script file description, comments, add my code
"""
import functools
import os
import typing as t


@functools.lru_cache(maxsize=1)
def get_homedir() -> str:
    """determine home directory of current user"""

    home = ""
    sudo_user = os.environ.get("SUDO_USER", "")
    if sudo_user:
        try:
            from pwd import getpwnam

            home = getpwnam(sudo_user).pw_dir
        except ImportError:
            pass
    if not home:
        try:
            from pathlib import Path

            home = str(Path.home())
        except IOError:
            pass
    if not home:
        home = os.path.expanduser("~")
    if not home:
        home = os.environ.get("HOME", os.path.abspath("."))
    home = os.path.normpath(home)
    return home


def get_desktop() -> str:
    """get desktop location"""
    homedir = get_homedir()
    desktop = os.path.join(homedir, "Desktop")

    # search for .config/user-dirs.dirs in HOMEDIR
    ud_file = os.path.join(homedir, ".config", "user-dirs.dirs")
    if os.path.exists(ud_file):
        val = desktop
        with open(ud_file, "r") as fh:
            text = fh.readlines()
        for line in text:
            if "DESKTOP" in line:
                line = line.replace("$HOME", homedir)[:-1]
                val = line.split("=")[1]
                val = val.replace('"', "").replace("'", "")
        desktop = val
    return desktop


def get_start_menu() -> str:
    """get start menu location"""
    homedir = get_homedir()
    return os.path.join(homedir, ".local", "share", "applications")


def create_shortcut(
    target: t.Union[str, os.PathLike],
    exe_path: t.Union[str, os.PathLike],
    *,
    arguments: t.Union[str, t.Sequence[str]] = "",
    working_dir: t.Union[str, os.PathLike] = "",
    icon_path: t.Union[str, os.PathLike] = "",
    description: str = "",
) -> None:
    ...
    # fixme: implement this function
    # raise NotImplementedError("TODO: create_shortcut")
