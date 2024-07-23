"""
references:
ebarr: https://stackoverflow.com/questions/23947281/python-multiprocessing-redirect-stdout-of-a-child-process-to-a-tkinter-text
"""

import dataclasses
import logging
import typing
from pathlib import Path

import psutil
from platformdirs import user_runtime_dir

from .mvc import Controller, Model, View
from .model import WizardModel
from .view import WizardView

from antares_web_installer.app import App, InstallError

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class WizardController(Controller):
    source_dir: typing.Optional[Path] = None
    target_dir: typing.Optional[Path] = None
    shortcut: typing.Optional[bool] = True
    launch: typing.Optional[bool] = True

    server_path: typing.Optional[Path] = None
    log_path: typing.Optional[Path] = dataclasses.field(init=False)
    log_file: typing.Optional[Path] = dataclasses.field(init=False)
    app: App = dataclasses.field(init=False)

    def __post_init__(self):
        super().__init__()
        self.initialize_log_path()

    def initialize_log_path(self):
        self.log_path = Path(user_runtime_dir("AntaresWebInstaller", "RTE"))
        if not self.log_path.exists():
            msg = "No log directory found with path '{}'.".format(self.log_path)
            logger.warning(msg)
            try:
                self.log_path.mkdir(parents=True)
            except FileExistsError:
                logger.warning("Path '{}' already exists.".format(self.log_path))
            else:
                logger.info("Path '{}' successfully created.".format(self.log_path))
        tmp_file_name = "web-installer.log"

        self.log_file = self.log_path.joinpath(tmp_file_name)

        # check if file exists
        if self.log_file not in list(self.log_path.iterdir()):
            # if not, create it first
            with open(self.log_file, "w") as f:
                pass
            f.close()

    def init_model(self, **kwargs) -> Model:
        model = WizardModel(self)
        return model

    def init_view(self) -> View:
        return WizardView(self)

    def install(self):
        logger.debug("Initializing installer worker")

        self.app = App(
            source_dir=self.source_dir,
            target_dir=self.target_dir,
            shortcut=self.shortcut,
            launch=self.launch,
        )

        try:
            self.app.run()
        except InstallError as e:
            logger.error(e)
            self.view.raise_error(
                "The installation encountered an error. The target directory may have been "
                "corrupted. Please check its integrity and try again."
            )
        except psutil.NoSuchProcess as e:
            logger.error(e)
            self.view.raise_error(
                "The installation encountered an error. The installation encountered an error while "
                "scanning processes. Please retry later."
            )
        else:
            logger.debug("Launch installer worker")
            logger.debug("Installation complete")

            self.view.frames[self.view.current_index].event_generate("<<InstallationComplete>>")

    def save_target_dir(self, path: str):
        self.target_dir = Path(path)

    def save_options(self, shortcut, launch):
        self.shortcut = shortcut
        self.launch = launch
