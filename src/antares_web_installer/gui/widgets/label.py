from tkinter import ttk


class Header(ttk.Label):
    def __init__(self, parent, wraplength, *args, **kwargs):
        super().__init__(parent, text="", padding=5, wraplength=wraplength, *args, **kwargs)


class Body(ttk.Label):
    def __init__(self, parent, wraplength, *args, **kwargs):
        super().__init__(parent, text="", padding=5, wraplength=wraplength, *args, **kwargs)
