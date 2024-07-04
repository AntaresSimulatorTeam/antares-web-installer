import tkinter as tk
from tkinter import ttk

from .button import CancelBtn, BackBtn, NextBtn, FinishBtn


class ControlFrame(ttk.Frame):
    def __init__(self, parent: tk.Misc, window: tk.Tk, cancel_btn=True, back_btn=False, next_btn=False, install_btn=False, finish_btn=False, *args, **kwargs):
        super().__init__(master=parent, *args, **kwargs)

        self.label = ttk.Label(self, text=f"Version '0.0.1'")
        self.window = window

        self.btns = {}

        if cancel_btn:
            self.btns["cancel"] = CancelBtn(self)
        if next_btn:
            self.btns["next"] = NextBtn(self)
        if install_btn:
            self.btns["install"] = NextBtn(self, text='Install')
        if finish_btn:
            self.btns["finish"] = FinishBtn(self)
        if back_btn:
            self.btns["back"] = BackBtn(self)

        for btn in self.btns.values():
            btn.pack(side=tk.RIGHT, anchor=tk.E)


class ChangeFrame(ttk.Frame):
    """

    """
    def __init__(self, master: tk.Misc, window: tk.Tk, index: int, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.header = ttk.Frame(self)
        self.body = ttk.Frame(self)
        self.header.pack(side="top", fill="x")
        self.body.pack(side="top", fill="x")

        self.window = window
        self.index = index

    def get_next_frame(self):
        return self.index + 1

    def get_previous_frame(self):
        return self.index - 1


class WelcomeFrame(ChangeFrame):
    # label title
    # label description
    # side pic
    # button control
    def __init__(self, master: tk.Misc, window: tk.Tk, index: int, *args, **kwargs):
        super().__init__(master, window, index,  *args, **kwargs)

        # header content
        header_content = ttk.Label(self.header, text="Welcome to Antares Web Installer")
        header_content.pack(side="top", fill="x")

        # body content
        main_content = ttk.Label(self.body, text="The Setup Wizard will install Antares Web Server on your computer. "
                                                 "Click Next to continue or Cancel to exit the Setup Wizard.")
        main_content.pack(side="top", fill="x")

        # control_btn
        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, back_btn=True, next_btn=True)
        self.control_btn.btns.get("back").toggle_btn(False)
        self.control_btn.pack(side="bottom", fill="x")


class PathChoicesFrame(ChangeFrame):
    def __init__(self, master: tk.Misc, window: tk.Tk, index: int, *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)

        target_path = tk.StringVar(value="/home/glaudemau/",)
        body_content = tk.Entry(self, textvariable=target_path, )
        body_content.pack(side="top", fill="x")

        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, back_btn=True, next_btn=True)
        self.control_btn.pack(side="bottom", fill="x")


class OptionChoicesFrame(ChangeFrame):
    def __init__(self, master: tk.Misc, window: tk.Tk, index: int,
                 *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)
        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, back_btn=True, install_btn=True)
        self.control_btn.pack(side="bottom", fill="x")


class ProgressFrame(ChangeFrame):
    def __init__(self, master: tk.Misc, window: tk.Tk, index: int,
                 *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)
        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, next_btn=True)
        self.control_btn.pack(side="bottom", fill="x")


class CongratulationFrame(ChangeFrame):
    def __init__(self, master: tk.Misc, window: tk.Tk, index: int, *args, **kwargs):
        super().__init__(master, window, index,  *args, **kwargs)
        self.control_btn = ControlFrame(parent=self, window=window, finish_btn=True)
        self.control_btn.pack(side="bottom", fill="x")

