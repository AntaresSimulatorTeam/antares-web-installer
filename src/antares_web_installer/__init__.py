import logging
import sys
from pathlib import Path

from platformdirs import user_data_dir

TARGET_DIR = Path(user_data_dir("AntaresWeb", "RTE"))
SRC_DIR = Path(".")

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)-15s] %(message)s", stream=sys.stdout)

logger = logging.getLogger(__name__)
