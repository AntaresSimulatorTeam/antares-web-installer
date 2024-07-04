import tkinter as tk
from tkinter import ttk
from typing import Tuple

from .mvc import View, Controller
from .widgets.frame import WelcomeFrame, PathChoicesFrame, OptionChoicesFrame, CongratulationFrame, ProgressFrame


class WizardView(View):
    def __init__(self, controller: Controller):
        super().__init__(controller)

        # configure window settings
        self.title('Antares Web Installer')
        self.width = 250
        self.height = 200

        self.set_geometry(self.width, self.height)

        # initialize main frame that contains all other frames
        container = ttk.Frame(self)
        container.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        frame_classes = [
            WelcomeFrame,
            PathChoicesFrame,
            OptionChoicesFrame,
            ProgressFrame,
            CongratulationFrame,
        ]
        self.frames = []
        for index, frame_class in enumerate(frame_classes):
            self.frames.append(frame_class(container, self, index))
            self.frames[index].grid(row=0, column=0, sticky=tk.NSEW)

        # initialize index of the first frame to be displayed
        self._current_index = 0
        self.change_frame()

    @property
    def current_index(self) -> int:
        return self._current_index

    @current_index.setter
    def current_index(self, new_index: int):
        self._current_index = new_index
        self.change_frame()

    def set_geometry(self, width, height):
        pixels = self.winfo_fpixels("9p")

        du_width = int((pixels / 4) * width)
        du_height = int((pixels / 4) * height)

        center_x = int((self.winfo_screenwidth() / 2) - (du_width / 2))
        center_y = int((self.winfo_screenheight() / 2) - (du_height / 2))

        self.geometry(f"{du_width}x{du_height}+{center_x}+{center_y}")

    def change_frame(self):
        # control btns
        self.frames[self.current_index].tkraise()
