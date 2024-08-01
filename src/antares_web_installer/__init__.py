import logging
from pathlib import Path

from platformdirs import user_data_dir

from antares_web_installer.shortcuts import get_homedir

SRC_DIR = Path("/home/glaudemau/bin/AntaresWeb-ubuntu-v2.17.1")
TARGET_DIR = Path(user_data_dir("AntaresWeb", "RTE"))

logger = logging.getLogger(__name__)
