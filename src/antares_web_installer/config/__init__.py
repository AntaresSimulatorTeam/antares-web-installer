"""
Module to update configuration files
"""

from pathlib import Path

import yaml

from antares_web_installer.config.config_2_19 import update_to_2_19


def update_config(source_path: Path, target_config_path: Path, version: str) -> None:
    """
    Update the configuration file to the latest version.

    :param source_path: source configuration file.
    :param target_config_path: target configuration file
    :param version: the current version of the application (e.g. "2.19").
    """

    with source_path.open(mode="r") as f:
        config = yaml.safe_load(f)

    version_info = tuple(map(int, version.split(".")))
    if version_info < (2, 19):
        update_to_2_19(config)

    with target_config_path.open(mode="w") as f:
        yaml.dump(config, f)
