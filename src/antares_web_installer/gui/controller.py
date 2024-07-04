import dataclasses
import os
from pathlib import Path

from .mvc import Controller, Model, View
from .model import WizardModel
from .view import WizardView


@dataclasses.dataclass
class WizardController(Controller):
    source_dir: Path = None
    target_dir: Path = None
    os_name: str = os.name
    shortcut: bool = True
    launch: bool = True
    browser: bool = True

    server_path: Path = None

    def __post_init__(self):
        super().__init__()

    def init_model(self, **kwargs) -> Model:
        model = WizardModel(self)
        return model

    def init_view(self) -> View:
        return WizardView(self)
