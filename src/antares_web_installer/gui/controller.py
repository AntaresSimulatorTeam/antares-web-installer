"""
references:
ebarr: https://stackoverflow.com/questions/23947281/python-multiprocessing-redirect-stdout-of-a-child-process-to-a-tkinter-text
"""

import typing
from pathlib import Path
from threading import Thread
from typing import Optional

from antares_web_installer.gui.mvc import Controller, ControllerError
from antares_web_installer.gui.model import WizardModel
from antares_web_installer.gui.view import WizardView

from antares_web_installer import logger
from antares_web_installer.app import App, InstallError
from antares_web_installer.gui.logger import ConsoleHandler, ProgressHandler, LogFileHandler


class InstallationThread(Thread):
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, *, daemon=None):
        super().__init__(group, target, name, args, kwargs, daemon=daemon)

    def run(self):
        try:
            super().run()
        except OSError as e:
            raise e
        except InstallError as e:
            raise e


class WizardController(Controller):
    """
    Must intercept all logic errors.
    Attribute:
        app: installation application
    """

    def __init__(self):
        super().__init__()
        self.app = None
        self.log_dir: Optional[Path] = None
        self.log_file: Optional[Path] = None

        # init loggers
        self.logger = logger

        # Thread used while installation is running
        self.thread = None
        # self.init_file_handler()

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
        self.log_dir : Path = self.model.target_dir / "logs"
        tmp_file_name = "wizard.log"

        if not self.log_dir.exists():
            self.log_dir = self.model.source_dir / "logs"  # use the source directory as tmp dir for logs
            self.logger.debug(
                "No log directory found with path '{}'. Attempt to generate the path.".format(self.log_dir)
            )
            self.log_dir.mkdir(parents=True, exist_ok=True)
            self.logger.info("Path '{}' was successfully created.".format(self.log_dir))

        self.log_file = self.log_dir / tmp_file_name

        # check if file exists
        if self.log_file not in list(self.log_dir.iterdir()):
            # if not, create it first
            with open(self.log_file, "a") as f:
                pass
            f.close()

    def init_log_file_handler(self):
        self.init_file_handler()
        log_file_handler = LogFileHandler(self.log_file)
        self.logger.addHandler(log_file_handler)

    # initialize file handler logger
    def init_console_handler(self, callback):
        """

        @param callback:
        @return:
        """
        console_handler = ConsoleHandler(callback)
        self.logger.addHandler(console_handler)

    def init_progress_handler(self, callback):
        """
        Initialize handler log of progress.
        The logs generated will be shown on the window console during installation
        @param callback: function that is used to update logs
        """
        progress_logger = ProgressHandler(callback)
        self.logger.addHandler(progress_logger)

    def run(self) -> None:
        """
        start program
        @return:
        """
        self.view.update_view()
        super().run()

    def install(self, callback: typing.Callable):
        """
        Run App.install method
        @param callback: function that is used to update logs
        """
        self.init_log_file_handler()
        self.logger.debug("file logger initialized.")
        self.init_console_handler(callback)
        self.logger.debug("console logger initialized.")
        self.init_progress_handler(callback)
        self.logger.debug("progress logger initialized.")

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

        thread = InstallationThread(target=self.app.run, args=())

        try:
            thread.start()
        except InstallError as e:
            self.view.raise_error(e)

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
        result = self.model.set_target_dir(path)
        if not result:
            raise ControllerError("Path '{}' is not a directory.".format(path))

    def get_shortcut(self) -> bool:
        return self.model.shortcut

    def set_shortcut(self, new_value):
        self.model.set_shortcut(new_value)

    def get_launch(self) -> bool:
        return self.model.launch

    def set_launch(self, new_value):
        self.model.set_launch(new_value)

    def update_log_file(self):
        # close log file handler
        logger.debug("Terminate log file handler.")
        log_file_handler = logger.handlers[0]

        log_file_handler.flush()
        log_file_handler.close()

        logger.removeHandler(log_file_handler)
        logger.debug("Log file handler was successfully removed")

        # If log file was newly created, it is located in source dir
        if self.log_file.parent.parent == self.model.source_dir:
            # move log file into Antares logs directory
            new_log_file_path = self.get_target_dir().joinpath(self.log_file.parent.name, self.log_file.name)
            try:
                self.log_file.replace(new_log_file_path)
            except FileNotFoundError as e:
                if new_log_file_path.exists():
                    logger.debug("Log file '{}' was already moved. Skip renaming step.".format(new_log_file_path))
                else:
                    logger.debug("Error while moving log file: {}".format(e))
            except PermissionError as e:
                logger.debug("Impossible to move log file: {}".format(e))
