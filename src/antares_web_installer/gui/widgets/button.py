import tkinter as tk
from tkinter import ttk, messagebox
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from antares_web_installer.gui.widgets.frame import ControlFrame


class BaseButton(ttk.Button):
    def __init__(self, parent: 'ControlFrame', text: str, command=Callable):
        super().__init__(master=parent, text=text, command=command)

    def toggle_btn(self, value: bool):
        if value:
            self.state(['!disabled'])
        else:
            self.state(['disabled'])


class ChangeFrameButton(BaseButton):
    def __init__(self, parent: 'ControlFrame', text: str):
        super().__init__(parent, text=text, command=self.change_frame)

    def change_frame(self):
        pass


class CloseableButton(BaseButton):
    def __init__(self, parent: 'ControlFrame', text: str, command=Callable):
        super().__init__(parent, text, command)

    def close_window(self):
        self.master.window.destroy()


class NextBtn(ChangeFrameButton):
    def __init__(self, parent: 'ControlFrame', text='Next'):
        super().__init__(parent, text=text)

    def change_frame(self):
        self.master.window.current_index += 1


class BackBtn(ChangeFrameButton):
    def __init__(self, parent: 'ControlFrame', text='Back'):
        super().__init__(parent, text=text)

    def change_frame(self):
        self.master.window.current_index -= 1


class CancelBtn(CloseableButton):
    def __init__(self, parent: 'ControlFrame'):
        super().__init__(parent, text="Cancel", command=self.confirm)

    def confirm(self):
        answer = messagebox.askyesno("Quit application",
                                     "Are you sure you want to cancel the installation?")
        if answer:
            self.close_window()


class FinishBtn(CloseableButton):
    def __init__(self, parent: 'ControlFrame'):
        super().__init__(parent, text="Finish", command=self.close_window)
