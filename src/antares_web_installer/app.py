import dataclasses
import os
from pathlib import Path

import psutil

from antares_web_installer.installer import install


@dataclasses.dataclass
class App:
    source_dir: Path
    target_dir: Path
    app_name: str = "AntaresWebInstaller"
    os_name: str = os.name

    # def __post_init__(self):
    #     self.source_dir = Path(self.source_dir)
    #     self.target_dir = Path(self.target_dir)

    def install(self) -> None:
        self.server_running_handler()
        self.install_files()
        self.create_icons()
        self.start_server()
        self.open_web_browser()

    def server_running_handler(self) -> None:
        """
        Check whether antares service is up.
        In case it is, terminate the process
        """
        for proc in psutil.process_iter(["pid", "name"]):
            if self.app_name in proc.name():
                print("Cannot upgrade since the application is running.")

                running_app = psutil.Process(pid=proc.pid)
                running_app.kill()  # ... or terminate ?
                running_app.wait(30)
                assert not running_app.is_running()

                print("The application was successfully stopped.")
                return

    def install_files(self):
        install(self.source_dir, self.target_dir)

    def create_icons(self):
        pass

    def start_server(self):
        pass

    def open_web_browser(self):
        pass
