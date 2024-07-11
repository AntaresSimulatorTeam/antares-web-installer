import tkinter as tk
from tkinter import ttk, font
from typing import TYPE_CHECKING

from .mvc import View

if TYPE_CHECKING:
    from .controller import WizardController
from .widgets.frame import WelcomeFrame, PathChoicesFrame, OptionChoicesFrame, CongratulationFrame, ProgressFrame
from .widgets import convert_in_du


class WizardView(View):
    def __init__(self, controller: "WizardController"):
        super().__init__(controller)

        # configure window settings
        self.title("Antares Web Installer")
        self.width, self.height = self.set_geometry(250, 200)
        self.resizable(False, False)
        self.current_log = ""

        # set styles
        self.initialize_styles()

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
        ttk.Style().configure("Title.TLabel", padding=(11, 11), wraplength=self.width, font=(current_font, 20))
        # description
        ttk.Style().configure("Description.TLabel", padding=(11, 5), wraplength=self.width, font=(current_font, 10))

    def change_frame(self):
        """
        @return:
        """
        frame = self.frames[self.current_index]
        frame.tkraise()
        frame.update()
        frame.update_idletasks()
        frame.event_generate("<<ActivateFrame>>")
