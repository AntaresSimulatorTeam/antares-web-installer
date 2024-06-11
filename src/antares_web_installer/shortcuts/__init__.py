import typing as t
import importlib
import os
import sys

_PKG = "antares_web_installer.shortcuts"

# https://stackoverflow.com/a/13874620/1513933
_shell_module = importlib.import_module(f"_{sys.platform}_shell", _PKG)


def get_homedir() -> str:
    return _shell_module.get_homedir()


def get_desktop() -> str:
    return _shell_module.get_desktop()


def get_start_menu() -> str:
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
