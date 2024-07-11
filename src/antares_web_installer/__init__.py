import logging
from pathlib import Path
from antares_web_installer.shortcuts import get_homedir

TARGET_DIR = Path(get_homedir()).joinpath("AntaresWeb")
SRC_DIR = Path(".")

logger = logging.getLogger(__name__)
