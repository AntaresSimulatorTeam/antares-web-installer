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


if __name__ == '__main__':
    # Créer la fenêtre principale
    root = tk.Tk()

    # Attendre que la fenêtre soit mise à jour pour obtenir des mesures précises
    root.update_idletasks()

    du = DialogUnit(root)

    # Convertir les unités de dialogue en pixels
    width_px, height_px = du(317, 193)

    # Créer une nouvelle fenêtre de dialogue
    root.title("Message de bienvenue")

    # Définir la taille de la fenêtre de dialogue
    root.geometry(f"{width_px}x{height_px}")

    # Ajouter un message de bienvenue
    message = tk.Label(root, text="Bienvenue")
    message.pack(expand=True)

    # Exécuter l'application
    root.mainloop()
