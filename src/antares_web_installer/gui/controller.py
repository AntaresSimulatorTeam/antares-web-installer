"""
references:
ebarr: https://stackoverflow.com/questions/23947281/python-multiprocessing-redirect-stdout-of-a-child-process-to-a-tkinter-text
"""

import typing
from pathlib import Path
from threading import Thread

from antares_web_installer.gui.mvc import Controller, ControllerError
from antares_web_installer.gui.model import WizardModel
from antares_web_installer.gui.view import WizardView

from antares_web_installer import logger
from antares_web_installer.app import App, InstallError
from antares_web_installer.gui.logger import ConsoleHandler, ProgressHandler, LogFileHandler


class WizardController(Controller):
    """
    Must intercept all logic errors.
    Attribute:
        app: installation application
    """

    def __init__(self):
        super().__init__()
        self.app = None
        self.log_dir = None
        self.log_file = None

        # init loggers
        self.logger = logger

        # Thread used while installation is running
        self.thread = None
        self.init_file_handler()

    def init_model(self) -> "WizardModel":
        """
        Override Controller.init_model
        @return: a new WizardModel instance
        """
        return WizardModel(self)

    def init_view(self) -> "WizardView":
        """
        Override Controller.init_view
        @return: a new WizardView instance
        """
        return WizardView(self)

    def init_file_handler(self):
        self.log_dir = self.model.source_dir.joinpath("logs/")
        tmp_file_name = "wizard.log"

        if not self.log_dir.exists():
            self.logger.debug(
                "No log directory found with path '{}'. Attempt to generate the path.".format(self.log_dir)
            )
            try:
                self.log_dir.mkdir(parents=True)
            except FileExistsError:
                self.logger.warning("Path '{}' already exists. Skip creation step.".format(self.log_dir))
            else:
                self.logger.info("Path '{}' was successfully created.".format(self.log_dir))

        self.log_file = self.log_dir.joinpath(tmp_file_name)

        # check if file exists
        if self.log_file not in list(self.log_dir.iterdir()):
            # if not, create it first
            with open(self.log_file, "w") as f:
                pass
            f.close()

    def init_log_file_handler(self):
        log_file_handler = LogFileHandler(self.log_file)
        self.logger.addHandler(log_file_handler)

    # initialize file handler logger
    def init_console_handler(self, callback):
        console_handler = ConsoleHandler(callback)
        self.logger.addHandler(console_handler)

    def init_progress_handler(self, callback):
        progress_logger = ProgressHandler(callback)
        self.logger.addHandler(progress_logger)

    def run(self) -> None:
        self.view.update_view()
        super().run()

    def install(self, callback: typing.Callable):
        self.init_log_file_handler()
        self.init_console_handler(callback)
        self.init_progress_handler(callback)

        self.logger.debug("Initializing installer worker")

        try:
            self.app = App(
                source_dir=self.model.source_dir,
                target_dir=self.model.target_dir,
                shortcut=self.model.shortcut,
                launch=self.model.launch,
            )
        except InstallError as e:
            logger.warning("Impossible to create a new shortcut. Skip this step.")
            logger.debug(e)

        thread = Thread(target=self.app.run, args=())
        thread.start()

    def installation_over(self) -> None:
        """
        This method makes sure the thread terminated. If not, it waits for it to terminate.
        """
        if self.thread:
            while self.thread.join():
                if not self.thread.is_alive():
                    break

    def get_target_dir(self) -> Path:
        return self.model.target_dir

    def set_target_dir(self, path: Path):
        self.model.set_target_dir(path)  # errors ?

    def get_shortcut(self) -> bool:
        return self.model.shortcut

    def set_shortcut(self, new_value):
        self.model.set_shortcut(new_value)

    def get_launch(self) -> bool:
        return self.model.launch

    def set_launch(self, new_value):
        self.model.set_launch(new_value)

    def update_log_file(self):
        # move log file into Antares directory
        new_log_file_path = self.get_target_dir().joinpath(self.log_file.parent.name, self.log_file.name)
        try:
            self.log_file.rename(new_log_file_path)
        except FileNotFoundError as e:
            if new_log_file_path.exists():
                logger.debug("Log file '{}' was already moved. Skip renaming step.".format(new_log_file_path))
            else:
                logger.debug("Error while moving log file: {}".format(e))
                raise ControllerError("No log file found at: {}".format(e))
        except PermissionError as e:
            logger.debug("Impossible to move log file: {}".format(e))
