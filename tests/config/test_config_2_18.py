from pathlib import Path

import yaml

from antares_web_installer.config.config_2_18 import update_to_2_18


def test_update_to_2_18(datadir: Path) -> None:
    config = yaml.safe_load(datadir.joinpath("application-2.17.yaml").read_text())
    expected = yaml.safe_load(datadir.joinpath("application-2.18.yaml").read_text())
    update_to_2_18(config)
    assert config == expected
