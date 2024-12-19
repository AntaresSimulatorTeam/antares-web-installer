from pathlib import Path

import yaml

from antares_web_installer.config.config_2_19 import update_to_2_19


def test_update_to_2_19(datadir: Path) -> None:
    config = yaml.safe_load(datadir.joinpath("application-2.18.yaml").read_text())
    expected = yaml.safe_load(datadir.joinpath("application-2.19.yaml").read_text())
    update_to_2_19(config)
    assert config == expected
