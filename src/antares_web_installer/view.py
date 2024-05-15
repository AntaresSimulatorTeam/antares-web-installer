"""
views that manage window, frames and other visual components for
the user interface
"""
import tkinter as tk
from tkinter import ttk
from dataclasses import field, dataclass, InitVar


class View(ttk.Frame):
    """
    Current view
    """
    pass


class AbstractStyle(ttk.Style):
    """
    Abstract style for widgets
    """
    pass


class AbstractWidgetFrame(ttk.Frame):
    """
    Abstract frame that directly contains widgets
    Used by abstract container frames
    """
    pass


class AbstractContainerFrame(ttk.Frame):
    """
    Abstract frame that contains other frames
    Used by main window
    """
    pass


class HomeFrame(AbstractContainerFrame):
    """
    """
    style: ttk.Style = None
    header: ttk.Frame = None
    body: ttk.Frame = None
    footer: ttk.Frame = None
    side_img: tk.PhotoImage = None

    def __init__(self, window):
        super().__init__()

        self.header = ttk.Frame(window)
        self.header.grid(column=0, row=0, sticky="nsew")
        header_content = ttk.Label(self.header, text="header")
        header_content.pack(side=tk.TOP, expand=True, padx=7, pady=(7, 0), ipadx=7, ipady=7)

        self.body = ttk.Frame(window)
        self.body.grid(column=0, row=1, sticky="nsew", padx=7, pady=(7, 0), ipadx=7, ipady=7)

        body_style = ttk.Style(self.body)
        body_style.configure('BodyFrame.TFrame', background='white')

        self.body.configure(borderwidth=5, relief="solid", style='BodyFrame.TFrame')

        side = ttk.Frame(self.body, style='BodyFrame.TFrame')
        side.pack(side=tk.LEFT)

        self.side_img = tk.PhotoImage(file="../../docs/assets/galaxy-side-1-ratio.png")

        side_content = ttk.Label(side, image=self.side_img, borderwidth=2, relief="sunken")
        side_content.pack(side=tk.LEFT, expand=False)

        # Main Frame
        main = ttk.Frame(self.body, style='BodyFrame.TFrame')
        main.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        main_title = ttk.Label(main, text="Welcome to Antares Web Installer")
        main_title.pack()

        main_description = ttk.Label(main, text="This wizard will guide you trhough the installation of Antares Web.")
        main_description.pack()

        self.footer = ttk.Frame(window)
        self.footer.grid(column=0, row=2, sticky="nsew", padx=7, pady=(7, 0), ipadx=7, ipady=7)

        # Buttons
        buttons = dict()

        # Cancel
        buttons["cancel"] = ttk.Button(master=self.footer, text="Cancel", command=window.quit)
        buttons["cancel"].pack(side=tk.RIGHT, padx=(10, 20))

        # Next
        buttons["next"] = ttk.Button(master=self.footer, text="Next")
        buttons["next"].pack(side=tk.RIGHT)

        # Back
        buttons["back"] = ttk.Button(master=self.footer, text="Back")
        buttons["back"].pack(side=tk.RIGHT)


class LicenseAgreementFrame(AbstractContainerFrame):
    pass


class IconCreationFrame(AbstractContainerFrame):
    pass


class DirectoryChoiceFrame(AbstractContainerFrame):
    pass


class InstallationFrame(AbstractContainerFrame):
    pass


class ConfirmationFrame(AbstractContainerFrame):
    pass


@dataclass
class Window(tk.Tk):
    """
    Root window of the application
    """
    step_list: list = field(init=False, default=None)

    def __init__(self):
        super().__init__()
        self.initial_config()

        self.step_list = []
        self.step_list.append(HomeFrame(self))

    def initial_config(self) -> None:
        # dimension
        width = 640
        height = 480
        pos_x = int(self.winfo_screenwidth()/2) - int(width/2)
        pos_y = int(self.winfo_screenheight()/2) - int(height/2)
        self.geometry(f"{width}x{height}+{pos_x}+{pos_y}")

        # grid configuration
        self.rowconfigure(0, weight=1)  # header row
        self.rowconfigure(1, weight=1)  # main and side rows
        self.rowconfigure(2, weight=1)  # footer row

        self.columnconfigure(0, minsize=self.winfo_width())

        # other configs
        self.title("Antares Web Installer")
        self.resizable(False, False)
        self.iconbitmap('../../docs/assets/antares-web-installer-icon.ico')
