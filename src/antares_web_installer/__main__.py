"""
Main entrypoint for the CLI application.
"""
import sys

from antares_web_installer.cli import install_cli


def main():
    install_cli(sys.argv[1:])


if __name__ == '__main__':
    main()
