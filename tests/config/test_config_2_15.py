from pathlib import Path
from unittest.mock import patch

import pytest

from antares_web_installer.config import update_to_2_15

import yaml


@pytest.mark.parametrize("suffix", ["local", "slurm", "both"])
def test_update_to_2_15(datadir: Path, suffix: str) -> None:
    config = yaml.safe_load(datadir.joinpath(f"application-2.14.{suffix}.yaml").read_text())
    with patch("os.cpu_count", return_value=20):
        update_to_2_15(config)
    expected = yaml.safe_load(datadir.joinpath(f"application-2.15.{suffix}.yaml").read_text())
    if suffix in {"slurm", "both"}:
        expected["launcher"]["slurm"]["nb_cores"] = {"min": 1, "default": 12, "max": 20}
    assert config == expected
