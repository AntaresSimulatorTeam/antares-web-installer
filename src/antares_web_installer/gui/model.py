import logging

from pathlib import Path

from antares_web_installer.gui.mvc import Model, Controller
from antares_web_installer import SRC_DIR, TARGET_DIR

logger = logging.getLogger(__name__)


class ModelError(Exception):
    pass


class WizardModel(Model):
    """
    Optional attributes
    @param source_dir:
    @param target_dir:
    @param shortcut_dir:
    @param launch:
    """

    def __init__(self, controller: Controller):
        super().__init__(controller)
        self.source_dir = SRC_DIR
        self.target_dir = TARGET_DIR
        self.shortcut = True
        self.launch = True

    def set_target_dir(self, new_target_dir: Path) -> None:
        self.target_dir = new_target_dir

    def set_shortcut(self, new_shortcut: bool):
        self.shortcut = new_shortcut
        logger.debug("Shortcut option is now set to '{}'.".format(self.shortcut))

    def set_launch(self, new_launch: bool):
        self.launch = new_launch
        logger.debug("Launch option is now set to '{}'.".format(self.shortcut))
