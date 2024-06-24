from pathlib import Path
from unittest.mock import patch
from antares_web_installer.config import update_to_2_15

import yaml


def test_update_to_2_15(datadir: Path):
    config = yaml.safe_load(datadir.joinpath("application-2.14.yaml").read_text())
    with patch("os.cpu_count", return_value=20):
        update_to_2_15(config)
    expected = yaml.safe_load(datadir.joinpath("application-2.15.yaml").read_text())
    expected["launcher"]["slurm"]["nb_cores"] = {"min": 1, "default": 12, "max": 20}
    assert config == expected
