import logging
from pathlib import Path

from platformdirs import user_data_dir

TARGET_DIR = Path(user_data_dir("AntaresWeb", "RTE"))
SRC_DIR = Path("/home/glaudemau/bin/AntaresWeb-ubuntu-v2.17.5/")

logger = logging.getLogger(__name__)
