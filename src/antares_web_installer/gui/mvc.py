"""
Model View Controller module.
Defines base classes for MVC architecture.
"""

from __future__ import annotations

import tkinter as tk
import traceback
from tkinter import messagebox


class Model:
    """
    Base class of the MVC model.

    Attributes:
        controller: The controller of the MVC.
    """

    def __init__(self, controller: Controller):
        self.controller = controller


class ViewError(Exception):
    pass


class View(tk.Tk):
    """
    Base class of the MVC view.

    Attributes:
        controller: The controller of the MVC.
    """

    def __init__(self, controller: Controller):
        super().__init__()
        self.controller = controller
        self.report_callback_exception = self.show_error

    def show_error(self, *args):
        err = traceback.format_exception(*args)
        messagebox.showerror("Exception", "".join(err))


class Controller:
    """
    Base class of the MVC controller.

    Attributes:
        model: The model of the MVC.
        view: The view of the MVC.
    """

    def __init__(self):
        self.model = self.init_model()
        self.view = self.init_view()

    def init_model(self) -> Model:
        return Model(self)

    def init_view(self) -> View:
        return View(self)

    def run(self) -> None:
        self.view.mainloop()

    def quit(self) -> None:
        self.view.destroy()
