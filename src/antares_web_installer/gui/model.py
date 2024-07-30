import dataclasses
import logging
import typing

from pathlib import Path

from platformdirs import user_data_dir

from .mvc import Model


logger = logging.getLogger(__name__)


class ModelError(Exception):
    pass


@dataclasses.dataclass
class WizardModel(Model):
    """
        Optional attributes
        @param source_dir:
        @param target_dir:
        @param shortcut_dir:
        @param launch:
    """
    source_dir: typing.Optional[Path] = None
    target_dir: typing.Optional[Path] = None
    shortcut: typing.Optional[bool] = True
    launch: typing.Optional[bool] = True

    def __init__(self, controller):
        super().__init__(controller)
        self.source_dir = Path("/home/glaudemau/bin/AntaresWeb-ubuntu-v2.17.1")  # TODO: To change
        self.target_dir = Path(user_data_dir("AntaresWeb", "RTE"))

    def set_target_dir(self, new_target_dir: typing.Optional[Path]):
        if not self.target_dir.exists():
            logger.error("Target directory '{}' does not exist.".format(self.target_dir))
        else:
            self.target_dir = new_target_dir

    def set_shortcut(self, new_shortcut: bool):
        self.shortcut = new_shortcut
        logger.debug("Shortcut option is now set to '{}'.".format(self.shortcut))

    def set_launch(self, new_launch: bool):
        self.launch = new_launch
        logger.debug("Launch option is now set to '{}'.".format(self.shortcut))
