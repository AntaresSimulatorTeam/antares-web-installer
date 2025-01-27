"""
Main entrypoint for the GUI application.
"""

import logging
import sys

from antares_web_installer.gui.controller import WizardController


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)-15s] %(message)s",
        stream=sys.stdout,
    )

    controller = WizardController()
    controller.run()


if __name__ == "__main__":
    main()
