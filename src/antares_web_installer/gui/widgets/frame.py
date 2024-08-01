import tkinter as tk
import typing
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING

from antares_web_installer.shortcuts import get_homedir
from .button import CancelBtn, BackBtn, NextBtn, FinishBtn, InstallBtn

if TYPE_CHECKING:
    from antares_web_installer.gui.view import WizardView

FORMAT = "[%(asctime)-15s] %(message)s"


class ViewError(Exception):
    pass


class ControlFrame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        window: tk.Tk,
        cancel_btn: bool = True,
        back_btn: bool = False,
        next_btn: bool = False,
        install_btn: bool = False,
        finish_btn: bool = False,
        *args,
        **kwargs,
    ):
        super().__init__(master=parent, **kwargs)

        self.label = ttk.Label(self, text="Version '0.0.1'")
        self.window = window

        self.btns: typing.Dict[str, typing.Union[CancelBtn, NextBtn, InstallBtn, FinishBtn, BackBtn]] = {}

        if cancel_btn:
            self.btns["cancel"] = CancelBtn(self)
        if next_btn:
            self.btns["next"] = NextBtn(self)
        if install_btn:
            self.btns["install"] = InstallBtn(self)
        if finish_btn:
            self.btns["finish"] = FinishBtn(self)
        if back_btn:
            self.btns["back"] = BackBtn(self)

        for btn in self.btns.values():
            btn.pack(side=tk.RIGHT, anchor=tk.E)


class BasicFrame(ttk.Frame):
    """
    Basic class for every frame of the project
    @attribute master:
    @attribute window:
    @attribute header:
    @attribute body:
    """

    def __init__(self, master: tk.Misc, window: "WizardView", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.header = ttk.Frame(self)
        self.body = ttk.Frame(self)
        self.header.pack(side="top", fill="x")
        self.body.pack(side="top", fill="x")

        self.window = window


class WelcomeFrame(BasicFrame):
    # label title
    # label description
    # side pic
    # button control
    def __init__(self, master: tk.Misc, window: "WizardView", *args, **kwargs):
        super().__init__(master, window, *args, **kwargs)
        # header content
        header_content = ttk.Label(self.header, text="Welcome to Antares Web Installer", style="Title.TLabel")
        header_content.pack(side="top", fill="x")

        # body content
        body_content = ttk.Label(
            self.body,
            text="The Setup Wizard will install Antares Web Server on your computer. "
            "Click Next to continue or Cancel to exit the Setup Wizard.",
            style="Description.TLabel",
        )
        body_content.pack(side="top", fill="x")

        # control_btn
        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, back_btn=True, next_btn=True)

        back_btn = self.control_btn.btns.get("back")
        if back_btn is not None:
            back_btn.toggle_btn(False)
        else:
            # error to raise
            pass

        self.control_btn.pack(side="bottom", fill="x")


class PathChoicesFrame(BasicFrame):
    """
    see https://learn.microsoft.com/en-us/windows/win32/uxguide/vis-layout
    """

    def __init__(self, master: tk.Misc, window: "WizardView", *args, **kwargs):
        super().__init__(master, window, *args, **kwargs)
        # Lazy import for typing and testing

        self.body.grid_rowconfigure(0, weight=1)
        self.body.grid_rowconfigure(1, weight=1)
        self.body.grid_columnconfigure(index=0, weight=4)
        self.body.grid_columnconfigure(index=1, weight=1)

        title_content = ttk.Label(self.header, text="Installation location", style="Title.TLabel")
        title_content.pack(side="top", fill="x")

        description = ttk.Label(
            self.body, text="The Antares Web Installer will be in the following directory: ", style="Description.TLabel"
        )
        description.grid(column=0, row=0, sticky="w")

        self.target_path = tk.StringVar(
            value="",
        )
        target_entry = tk.Entry(
            self.body,
            textvariable=self.target_path,
            width=int(len(self.target_path.get()) + 6.9),  # windows layout conventions
        )
        target_entry.grid(column=0, row=1, sticky="nsew")

        browse_btn = ttk.Button(self.body, text="Browse", command=self.browse)
        browse_btn.grid(column=1, row=1, sticky="nsew")

        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, back_btn=True, next_btn=True)
        self.control_btn.btns["next"].configure(command=self.get_next_frame)
        self.control_btn.pack(side="bottom", fill="x")

        self.bind("<<ActivateFrame>>", self.on_active_frame)

    def on_active_frame(self, event):
        self.target_path.set(str(self.window.get_target_dir()))

    def browse(self):  # TODO: staticmethod ?
        dir_name = filedialog.askdirectory(
            title="Choose the target directory",
            initialdir=get_homedir(),
        )
        self.target_path.set(dir_name)

    def get_next_frame(self):
        # Lazy import for typing and testing purposes

        # save new target_dir
        self.window.set_target_dir(self.target_path.get())
        next_btn = self.control_btn.btns.get("next")
        if next_btn:
            self.control_btn.btns["next"].change_frame()
        else:
            # error to raise
            pass


class OptionChoicesFrame(BasicFrame):
    def __init__(self, master: tk.Misc, window: "WizardView", *args, **kwargs):
        super().__init__(master, window, *args, **kwargs)

        ttk.Label(self.header, text="Select installation options", style="Title.TLabel")

        ttk.Label(self.header, text="Choose whether to apply these installation options.", style="Description.TLabel")

        self.is_shortcut = tk.BooleanVar(value=False)
        self.is_launch = tk.BooleanVar(value=False)

        ttk.Checkbutton(self.body, text="Create shortcut on Desktop", variable=self.is_shortcut).pack(
            side="top", fill="x"
        )
        ttk.Checkbutton(
            self.body, text="Launch Antares Web at the end of the installation", variable=self.is_launch
        ).pack(side="top", fill="x")

        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, back_btn=True, install_btn=True)
        self.control_btn.btns["install"].configure(command=self.get_next_frame)
        self.control_btn.pack(side="bottom", fill="x")

        self.bind("<<ActivateFrame>>", self.on_active_frame)

    def on_active_frame(self, event):
        self.is_shortcut.set(self.window.get_shortcut())
        self.is_launch.set(self.window.get_launch())

    def get_next_frame(self):
        """ """
        self.window.set_shortcut(self.is_shortcut.get())
        self.window.set_launch(self.is_launch.get())
        self.control_btn.btns["install"].change_frame()


class ProgressFrame(BasicFrame):
    def __init__(self, master: tk.Misc, window: "WizardView", *args, **kwargs):
        super().__init__(master, window, *args, **kwargs)
        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, next_btn=True)
        self.control_btn.pack(side="bottom", fill="x")

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self.body,
            orient="horizontal",
            mode="determinate",
            length=355,
        )
        self.progress_bar.pack(side="top", fill="x", padx=5, pady=5)

        # Progress Bar values
        self.progress_var = tk.StringVar(value="Progress: 0%")
        ttk.Label(self.body, textvariable=self.progress_var, style="Description.TLabel").pack(
            side="top", fill="x", padx=5
        )

        # Logs display
        self.console_var = tk.StringVar(value="")

        self.console = ttk.Label(
            self.body, textvariable=self.console_var, wraplength=window.width, style="Description.TLabel"
        )
        self.console.pack(side="top", fill="x", padx=5)

        # next btn is initially disabled
        self.control_btn.btns["next"].toggle_btn(False)

        self.bind("<<ActivateFrame>>", self.on_active_frame)

    def on_active_frame(self, event):
        self.window.run_installation(self.progress_update)

    def progress_update(self, logs: str):
        if logs.startswith("Progression: "):
            # progress bar description
            self.progress_var.set(logs + "%")

            # progress bar value
            progress_value = float(logs.lstrip("Progression: "))
            self.progress_bar["value"] = progress_value

            # in case installation is complete
            if progress_value == 100:
                self.window.installation_over()
        else:
            # console logs
            self.console_var.set(logs)
        self.window.update_idletasks()

    def installation_over(self):
        self.window.update_log_file()
        self.control_btn.btns["next"].toggle_btn(True)


class CongratulationFrame(BasicFrame):
    def __init__(self, master: tk.Misc, window: "WizardView", *args, **kwargs):
        super().__init__(master, window, *args, **kwargs)

        ttk.Label(self.header, text="Congratulations!", style="Title.TLabel").pack(side="top", fill="x")

        ttk.Label(
            self.body,
            text="The installation was successfully completed. You can now click on the Finish button "
            "to close this window.",
            style="Description.TLabel",
        ).pack(side="top", fill="x")

        self.control_btn = ControlFrame(parent=self, window=window, finish_btn=True)
        self.control_btn.pack(side="bottom", fill="x")
