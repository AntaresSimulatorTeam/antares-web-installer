"""
Main entrypoint for the GUI application.
"""

from antares_web_installer.gui.wizard_controller import WizardController


def main():
    controller = WizardController()
    controller.run()


if __name__ == "__main__":
    main()