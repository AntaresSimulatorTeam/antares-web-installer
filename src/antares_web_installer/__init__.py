import logging
from pathlib import Path

from platformdirs import user_data_dir

from antares_web_installer.shortcuts import get_homedir

TARGET_DIR = Path(user_data_dir("AntaresWeb", "RTE"))
SRC_DIR = Path(".")

logger = logging.getLogger(__name__)
