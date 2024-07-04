import tkinter as tk


class DialogUnit:
    """
    Dialog units are Windows' standard way of measuring distance on screen.

    Dialog units are defined as one-quarter the average character width by one-eighth
    the average character height of the default font used on a window
    (creating a roughly square unit of measurement).
    """

    def __init__(self, window):
        pixels = window.winfo_fpixels("9p")
        self.char_width = pixels / 4
        self.char_height = pixels / 4

    def __call__(self, width_du, height_du):
        return int(self.char_width * width_du), int(self.char_height * height_du)


if __name__ == "__main__":
    # Create the main window
    root = tk.Tk()

    # Wait for the window to be updated then get precise measurements
    root.update_idletasks()

    du = DialogUnit(root)

    # Convert du in px
    width_px, height_px = du(317, 193)

    # Add a title to the main window
    root.title("Message de bienvenue")

    # Resize main window
    root.geometry(f"{width_px}x{height_px}")

    # Add default message
    message = tk.Label(root, text="Bienvenue")
    message.pack(expand=True)

    # Launch application
    root.mainloop()
