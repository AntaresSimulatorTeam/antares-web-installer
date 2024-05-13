import dataclasses
import os
import psutil
import tkinter as tk

from tkinter import ttk
from pathlib import Path
from antares_web_installer.installer import install


@dataclasses.dataclass
class App:
    source_dir: Path
    target_dir: Path
    app_name: str = "AntaresWebInstaller"
    os_name: str = os.name
    window_width: int = 800
    window_height: int = 600

    # def __post_init__(self):
    #     self.source_dir = Path(self.source_dir)
    #     self.target_dir = Path(self.target_dir)

    def run(self) -> None:
        window = self.init_window()
        # self.server_running_handler()
        # self.install_files()
        # self.create_icons()
        # self.start_server()
        # self.open_web_browser()
        window.mainloop()

    def init_window(self) -> tk.Tk:
        window = tk.Tk()

        center_x = int(window.winfo_screenwidth()/2) - int(self.window_width/2)
        center_y = int(window.winfo_screenheight()/2) - int(self.window_height/2)

        window.title("Antares Web Installer")
        window.geometry(f"{self.window_width}x{self.window_height}+{center_x}+{center_y}")
        window.rowconfigure(0, minsize=int(self.window_height/5*4), weight=5)
        window.rowconfigure(1, minsize=int(self.window_height/5), weight=1)

        # Side Frame
        side = ttk.Frame(window)
        side.grid(column=0, row=0, rowspan=4)
        side['borderwidth'] = 3
        side['relief'] = 'solid'
        ttk.Label(side, text="Side", foreground="white", background="blue")

        # Main Frame
        main = ttk.Frame(window)
        main.grid(column=1, row=0, columnspan=1, rowspan=4)
        main['borderwidth'] = 3
        main['relief'] = 'solid'
        ttk.Label(main, text="Main", foreground="white", background="orange")


        # Footer Frame
        footer = ttk.Frame(window)
        footer.grid(column=0, row=1, columnspan=2, sticky="se", padx=5, pady=5)

        # Buttons
        buttons = dict()
        # Back
        buttons["Back"] = ttk.Button(master=footer, text="Back")
        # Next
        buttons["next"] = ttk.Button(master=footer, text="Next")
        # Cancel
        buttons["cancel"] = ttk.Button(master=footer, text="Cancel", command=window.destroy)

        for index, btn in enumerate(buttons.values()):
            btn.grid(column=index, row=0, sticky="se")
        return window

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
