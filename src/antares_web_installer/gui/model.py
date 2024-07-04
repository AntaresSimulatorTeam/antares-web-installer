import dataclasses

from .mvc import Model, Controller


class WizardModel(Model):
    def __init__(self, controller):
        super().__init__(controller)
