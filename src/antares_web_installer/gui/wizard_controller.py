from .mvc import Controller, Model, View
from .wizard_model import WizardModel
from .wizard_view import WizardView


class WizardController(Controller):
    def init_model(self) -> Model:
        return WizardModel(self)

    def init_view(self) -> View:
        return WizardView(self)
