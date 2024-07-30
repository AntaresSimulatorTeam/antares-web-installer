import logging
import typing


class ConsoleHandler(logging.Handler):
    def __init__(self, callback: typing.Callable = None):
        logging.Handler.__init__(self)
        self.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)-15s] %(message)s")
        self.setFormatter(formatter)
        self.callback = callback

    def emit(self, logs: logging.LogRecord):
        self.callback(logs.msg)


class ProgressHandler(logging.Handler):
    def __init__(self, callback: typing.Callable = None):
        """
        This logging handler intercept all logs that are progression values
        @param progress_var: tkinter.StringVar
        """
        logging.Handler.__init__(self)
        self.setLevel(logging.INFO)
        formatter = logging.Formatter("[%(asctime)-15s] %(message)s")
        self.setFormatter(formatter)
        self.callback = callback  # to call at the end of the emit() method

    def emit(self, logs: logging.LogRecord):
        self.callback(logs.msg)


class LogFileHandler(logging.FileHandler):
    def __init__(self, filename):
        super().__init__(filename, 'a')
        self.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
        self.setFormatter(formatter)
