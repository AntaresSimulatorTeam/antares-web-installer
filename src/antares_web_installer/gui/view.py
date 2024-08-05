"""
View module that defines the installer view named WizardView.

WizardView uses several custom frames that can be found in the `widgets.frame` module
WizardView displays elements using the Microsoft Display Unit as unit for spacing and placement.
"""

import logging
import tkinter as tk
import typing

from collections import OrderedDict
from pathlib import Path
from tkinter import ttk, font
from tkinter.messagebox import showerror, showwarning

from antares_web_installer.gui.mvc import View, ControllerError, ViewError
from antares_web_installer.gui.widgets.frame import (
    WelcomeFrame,
    PathChoicesFrame,
    OptionChoicesFrame,
    CongratulationFrame,
    ProgressFrame,
)
from antares_web_installer.gui.widgets import convert_in_du

if typing.TYPE_CHECKING:
    from antares_web_installer.gui.controller import WizardController


logger = logging.getLogger(__name__)


class WizardView(View):
    def __init__(self, controller: "WizardController"):
        """
        Installer view.

        ** Attributes **
        title: Title displayed on the top of the window
        width: Width of the window
        height: Height of the window
        frames: List of frames that must be displayed one by one, in the same order
        current_index: Index of the current frame

        @param controller: the Installer controller that must be a WizardController
        """
        super().__init__(controller)
        self.controller: "WizardController" = controller

        # configure window settings
        self.title("Antares Web Installer")
        self.width, self.height = self.set_geometry(250, 200)

        # set styles
        self.initialize_styles()

        # initialize index of the first frame to be displayed
        self.frames = OrderedDict()
        self._current_frame = "welcome_frame"

        self.resizable(False, False)

        # initialize main frame that contains all other frames
        container = ttk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames.update(
            {
                "welcome_frame": WelcomeFrame(container, self),
                "path_choice_frame": PathChoicesFrame(container, self),
                "option_choice_frame": OptionChoicesFrame(container, self),
                "progress_frame": ProgressFrame(container, self),
                "congratulation_frame": CongratulationFrame(container, self),
            }
        )

        for frame in self.frames.values():
            frame.grid(row=0, column=0, sticky=tk.NSEW)

        # self.change_frame()

    # Attribute accessors
    def get_next_frame(self):
        try:
            tmp_frame_list = list(self.frames.keys())
            new_frame = tmp_frame_list[tmp_frame_list.index(self._current_frame) + 1]
        except IndexError:
            logger.warning("No previous frame selected. Return the current_frame")
        else:
            self._current_frame = new_frame
        self.update_view()

    def get_previous_frame(self):
        try:
            tmp_frame_list = list(self.frames.keys())
            new_frame = tmp_frame_list[tmp_frame_list.index(self._current_frame) - 1]
        except IndexError:
            logger.warning("No previous frame selected. Return the current_frame")
        else:
            self._current_frame = new_frame
        self.update_view()

    def get_current_frame(self):
        return self.frames[self._current_frame]

    # Methods
    def set_geometry(self, width, height):
        """
        @param width:
        @param height:
        @return:
        """
        du_width = convert_in_du(self, width)
        du_height = convert_in_du(self, height)

        center_x = int((self.winfo_screenwidth() / 2) - (du_width / 2))
        center_y = int((self.winfo_screenheight() / 2) - (du_height / 2))

        self.geometry(f"{du_width}x{du_height}+{center_x}+{center_y}")

        return du_width, du_height

    def initialize_styles(self):
        """ """
        # default font
        current_font = font.nametofont("TkDefaultFont").actual()

        # titles
        ttk.Style().configure("Title.TLabel", padding=(11, 11), wraplength=self.width - 11 * 2, font=(current_font, 20))
        # description
        ttk.Style().configure(
            "Description.TLabel", padding=(11, 5), wraplength=self.width - 11 * 2, font=(current_font, 10)
        )

    def update_view(self):
        frame = self.frames[self._current_frame]
        frame.tkraise()
        frame = self.get_current_frame()
        frame.update_idletasks()
        frame.event_generate("<<ActivateFrame>>")

    def raise_error(self, msg):
        showerror("Error", msg)
        self.quit()

    def raise_warning(self, msg):
        showwarning("Warning", msg)

    def get_target_dir(self) -> Path:
        return self.controller.get_target_dir()

    def set_target_dir(self, new_target_dir: str):
        try:
            self.controller.set_target_dir(Path(new_target_dir))
        except ControllerError as e:
            logger.warning("Path is not valid: {}".format(e))
            self.raise_warning("Path selected is not valid")

    def get_launch(self) -> bool:
        return self.controller.get_launch()

    def set_shortcut(self, new_value: bool):
        self.controller.set_shortcut(new_value)

    def get_shortcut(self) -> bool:
        return self.controller.get_shortcut()

    def set_launch(self, new_value: bool):
        try:
            self.controller.set_launch(new_value)
        except AttributeError:
            raise ViewError("Controller is not a WizardController")

    def update_log_file(self):
        try:
            self.controller.update_log_file()
        except ControllerError:
            self.raise_error(
                "The application was successfully installed although a minor error occurred. You may "
                "continue or close the installer."
            )

    def run_installation(self, callback):
        self.controller.install(callback)

    def installation_over(self):
        self.controller.installation_over()
        self.frames["progress_frame"].installation_over()
