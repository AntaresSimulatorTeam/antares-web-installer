"""
references:
ebarr: https://stackoverflow.com/questions/23947281/python-multiprocessing-redirect-stdout-of-a-child-process-to-a-tkinter-text
"""

import dataclasses
import logging
import typing
from pathlib import Path

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
    app: App = dataclasses.field(init=False)

    def __post_init__(self):
        super().__init__()

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
            self.view.raise_error("The installation encountered an error. The target directory may have be corrupted. "
                                  "Please check its integrity and try again.")
        else:
            logger.debug("Launch installer worker")
            logger.debug("Installation complete")
            self.view.frames[self.view.current_index].event_generate("<<InstallationComplete>>")

    def save_target_dir(self, path: str):
        self.target_dir = Path(path)

    def save_options(self, shortcut, launch):
        self.shortcut = shortcut
        self.launch = launch
