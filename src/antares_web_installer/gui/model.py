from .mvc import Model


class WizardModel(Model):
    def __init__(self, controller):
        super().__init__(controller)
