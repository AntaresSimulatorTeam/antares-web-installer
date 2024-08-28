"""
Module to update configuration files
"""

from pathlib import Path

import yaml

from .config_2_15 import update_to_2_15


def update_config(source_path: Path, target_path: Path, version: str) -> None:
    """
    Update the configuration file to the latest version.

    :param source_path: source configuration file.
    :param target_path: target configuration file (if different from source).
    :param version: the current version of the application (e.g. "2.15").
    """

    with source_path.open(mode="r") as f:
        config = yaml.safe_load(f)

    version_info = tuple(map(int, version.split(".")))
    if version_info < (2, 15):
        try:
            update_to_2_15(config)
        except AttributeError:
            with target_path.open("r") as f:
                config = yaml.safe_load(f)

    with source_path.open(mode="w") as f:
        yaml.dump(config, f)
