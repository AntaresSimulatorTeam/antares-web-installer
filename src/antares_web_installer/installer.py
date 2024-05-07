import os
import subprocess
import textwrap
from pathlib import Path
from shutil import copy2, copytree, rmtree

from antares_web_installer import DEBUG

from antares_web_installer.config import update_config

# List of files and directories to exclude during installation
COMMON_EXCLUDED_FILES = {"config.prod.yaml", "config.yaml", "examples", "logs", "matrices", "tmp"}
POSIX_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker"}
WINDOWS_EXCLUDED_FILES = COMMON_EXCLUDED_FILES | {"AntaresWebWorker.exe"}
EXCLUDED_FILES = POSIX_EXCLUDED_FILES if os.name == "posix" else WINDOWS_EXCLUDED_FILES


class InstallError(Exception):
    """
    Exception that handles installation error
    """

    pass


def install(src_dir: Path, target_dir: Path) -> None:
    """ """
    # if "AntaresWeb/" directory already exists
    if target_dir.is_dir():
        # check app version
        version = check_version(target_dir)

        # update config file
        config_path = target_dir.joinpath("config.yaml")
        update_config(config_path, config_path, version)

        # copy binaries
        copy_files(src_dir, target_dir)

    else:
        # copy all files from package
        copytree(src_dir, target_dir)


def check_version(target_dir: Path) -> str:
    """
    Execute command to get the current version of the server.

    :param target_dir: path of target directory
    """
    # debug mode
    if DEBUG:
        exe_path = target_dir.joinpath("AntaresWeb/AntaresWebServer.py")
        args = ["python", exe_path, "--version"]
    else:
        exe_path = target_dir.joinpath("AntaresWeb/AntaresWebServer.exe")
        # check user's os
        if os.name.lower() == "posix":  # if os is linux, remove ".exe"
            exe_path.with_suffix("")
        args = [exe_path, "--version"]

    try:
        version = subprocess.check_output(args, text=True, stderr=subprocess.PIPE).strip()
    except FileNotFoundError as e:
        raise InstallError(f"Can't check version: {e}") from e
    except subprocess.CalledProcessError as e:
        reason = textwrap.indent(e.stderr, "  | ", predicate=lambda line: True)
        raise InstallError(f"Can't check version: {reason}")

    return version


def copy_files(src_dir: Path, target_dir: Path):
    """
    Copy all files from src_dir to target_dir
    Override existing files and directories that have the same name
    Raise an InstallError if an error occurs while overriding a directory, if the user hasn't the permission to write or
    if target_dir already exists.

    :param src_dir: location of directory to copy files from
    :param target_dir: location of directory to copy files to
    """
    for elt_path in src_dir.iterdir():
        if elt_path.name not in EXCLUDED_FILES:
            # verbose action ?
            try:
                if elt_path.is_file():
                    copy2(elt_path, target_dir)
                else:
                    # copytree() cannot natively override directory
                    # the target must be deleted first
                    rmtree(target_dir.joinpath(elt_path.name))

                    # check if the old directory is completely erased
                    if target_dir.joinpath(elt_path.name).exists():
                        raise InstallError(f"Erreur : Impossible de mettre à jour le répertoire {elt_path}")

                    # copy new directory
                    copytree(elt_path, target_dir.joinpath(elt_path.name))
            # handle permission errors
            except PermissionError:
                raise InstallError(f"Erreur : Impossible d'écrire dans {target_dir}")
            # handle other errors
            except BaseException as e:
                raise InstallError(f"{e}")
