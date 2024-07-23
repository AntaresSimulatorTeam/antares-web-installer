import logging
import os
import tkinter as tk
import typing
from threading import Thread
from tkinter import ttk, filedialog
from typing import TYPE_CHECKING

from antares_web_installer.shortcuts import get_homedir
from .button import CancelBtn, BackBtn, NextBtn, FinishBtn, InstallBtn

if TYPE_CHECKING:
    from antares_web_installer.gui.view import WizardView

FORMAT = "[%(asctime)-15s] %(message)s"


class ViewError(Exception):
    pass


class LogManager(logging.Handler):
    def __init__(self, progress_frame: "ProgressFrame"):
        logging.Handler.__init__(self)
        self.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)-15s] %(message)s")
        self.setFormatter(formatter)
        self.progress_frame = progress_frame

    def emit(self, logs: logging.LogRecord):
        content = logs.msg
        if content.startswith("Progression: "):
            current_progress = float(content.lstrip("Progression: "))
            self.progress_frame.current_progress.set(content + "%")
            self.progress_frame.progress_update(current_progress)
        else:
            self.progress_frame.current_logs.set(content)


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
    # TODO: fill the comment section
    Basic class for every frames of the project
    @attribute master:
    @attribute window:
    @attribute header:
    @attribute body:
    """

    def __init__(self, master: tk.Misc, window: "WizardView", index: int, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.header = ttk.Frame(self)
        self.body = ttk.Frame(self)
        self.header.pack(side="top", fill="x")
        self.body.pack(side="top", fill="x")

        self.window = window
        self.index = index


class WelcomeFrame(BasicFrame):
    # label title
    # label description
    # side pic
    # button control
    def __init__(self, master: tk.Misc, window: "WizardView", index: int, *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)
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

        self.control_btn.pack(side="bottom", fill="x")


class PathChoicesFrame(BasicFrame):
    """
    see https://learn.microsoft.com/en-us/windows/win32/uxguide/vis-layout
    """

    def __init__(self, master: tk.Misc, window: "WizardView", index: int, *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)
        # Lazy import for typing and testing
        from antares_web_installer.gui.controller import WizardController

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

        if isinstance(self.window.controller, WizardController):
            self.target_path = tk.StringVar(
                value=str(self.window.controller.target_dir),
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

    def browse(self):
        dir_name = filedialog.askdirectory(
            title="Choose the target directory",
            initialdir=get_homedir(),
        )
        self.target_path.set(dir_name)

    def get_next_frame(self):
        # Lazy import for typing and testing purposes
        from antares_web_installer.gui.controller import WizardController

        # save new target_dir
        if isinstance(self.window.controller, WizardController):
            self.window.controller.save_target_dir(self.target_path.get())  # FIXME
        next_btn = self.control_btn.btns.get("next")
        if next_btn:
            self.control_btn.btns["next"].change_frame()


class OptionChoicesFrame(BasicFrame):
    def __init__(self, master: tk.Misc, window: "WizardView", index: int, *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)
        # Lazy import for typing and testing purposes
        from antares_web_installer.gui.controller import WizardController

        ttk.Label(self.header, text="Select installation options", style="Title.TLabel")

        ttk.Label(self.header, text="Choose whether to apply these installation options.", style="Description.TLabel")

        if isinstance(self.window.controller, WizardController):
            self.is_shortcut = tk.BooleanVar(value=self.window.controller.shortcut)
            self.is_launch = tk.BooleanVar(value=self.window.controller.launch)

        ttk.Checkbutton(self.body, text="Create shortcut on Desktop", variable=self.is_shortcut).pack(
            side="top", fill="x"
        )
        ttk.Checkbutton(
            self.body, text="Launch Antares Web at the end of the installation", variable=self.is_launch
        ).pack(side="top", fill="x")

        self.control_btn = ControlFrame(parent=self, window=window, cancel_btn=True, back_btn=True, install_btn=True)
        self.control_btn.btns["install"].configure(command=self.get_next_frame)
        self.control_btn.pack(side="bottom", fill="x")

    def get_next_frame(self):
        """ """
        # Lazy import for typing and testing purposes
        from antares_web_installer.gui.controller import WizardController

        if isinstance(self.window.controller, WizardController):
            self.window.controller.save_options(self.is_shortcut.get(), self.is_launch.get())
        self.control_btn.btns["install"].change_frame()


class ProgressFrame(BasicFrame):
    def __init__(self, master: tk.Misc, window: "WizardView", index: int, *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)
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
        self.current_progress = tk.StringVar(value="Progress: 0%")
        ttk.Label(self.body, textvariable=self.current_progress, style="Description.TLabel").pack(
            side="top", fill="x", padx=5
        )

        # Logs display
        self.current_logs = tk.StringVar(value="")
        self.console = ttk.Label(
            self.body, textvariable=self.current_logs, wraplength=window.width, style="Description.TLabel"
        )
        self.console.pack(side="top", fill="x", padx=5)

        # next btn is initially disabled
        self.control_btn.btns["next"].toggle_btn(False)

        self.bind("<<ActivateFrame>>", self.on_active_frame)
        self.bind("<<InstallationComplete>>", self.on_installation_complete)

        # thread handling
        self.thread = None

    def progress_update(self, value: float):
        self.progress_bar["value"] = value

    def initialize_user_log_manager(self, logger):
        # One log after another is displayed in the main window
        log_manager = LogManager(self)
        logger.addHandler(log_manager)

    def initialize_file_log_manager(self, logger):
        from antares_web_installer.gui.controller import WizardController

        if isinstance(self.window.controller, WizardController):
            # create new tmp directory if it does not exist yet
            tmp_dir_path = self.window.controller.log_path
            tmp_file_name = "web-installer.log"

            tmp_file = tmp_dir_path.joinpath(tmp_file_name)

            # check if file exists
            if tmp_file not in list(tmp_dir_path.iterdir()):
                logger.info("No temporary file was found. Create a new one.")
                # if not, create it first

            if tmp_file.exists():
                logger.info("Creation successful")
            else:
                self.window.raise_error("No temporary file was created or found.")

    def on_active_frame(self, event):
        # Lazy import for typing and testing purposes
        from antares_web_installer.gui.controller import WizardController

        # retrieve app logger
        main_logger = logging.getLogger("antares_web_installer.app")

        # Initialize log manager
        log_manager = LogManager(self)
        main_logger.addHandler(log_manager)

        if isinstance(self.window.controller, WizardController):
            # redirect logs in the target `tmp` directory
            file_logger = logging.FileHandler(self.window.get_log_file())
            file_logger.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s: %(message)s"))
            file_logger.setLevel(logging.INFO)
            main_logger.addHandler(file_logger)

            # Launching installation in concurrency with the current process
            self.thread = Thread(target=self.window.controller.install, args=())
            self.thread.start()
        else:
            msg = "The installer encounters an issue while instantiating controller ('NotImplementedError')."
            main_logger.error(f"Not implemented {type(self.window.controller)}.")
            self.window.raise_error(msg)

    def on_installation_complete(self, event):
        # Lazy import for typing and testing purposes
        from antares_web_installer.gui.controller import WizardController

        if isinstance(self.window.controller, WizardController):
            # move log file in application log directory
            file_name = self.window.controller.log_file.name
            log_directory = self.window.controller.target_dir.joinpath('logs')
            self.window.get_log_file().rename(self.window.controller.target_dir.joinpath(log_directory, file_name))

        self.control_btn.btns["next"].toggle_btn(True)


class CongratulationFrame(BasicFrame):
    def __init__(self, master: tk.Misc, window: "WizardView", index: int, *args, **kwargs):
        super().__init__(master, window, index, *args, **kwargs)

        ttk.Label(self.header, text="Congratulations!", style="Title.TLabel").pack(side="top", fill="x")

        ttk.Label(
            self.body,
            text="The installation was successfully completed. You can now click on the Finish button "
            "to close this window.",
            style="Description.TLabel",
        ).pack(side="top", fill="x")

        self.control_btn = ControlFrame(parent=self, window=window, finish_btn=True)
        self.control_btn.pack(side="bottom", fill="x")
