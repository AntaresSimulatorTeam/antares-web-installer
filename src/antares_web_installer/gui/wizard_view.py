from .mvc import View


class WizardView(View):
    def init_window(self) -> None:
        super().init_window()
        self.title("Antares Web Installer")
