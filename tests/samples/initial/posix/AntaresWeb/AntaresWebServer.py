import os

import click

OLD_ANTARES_VERSION = os.environ.get("ANTARES_VERSION", "2.17")


@click.command()
@click.version_option(version=OLD_ANTARES_VERSION, message="%(version)s")
def cli():
    pass


if __name__ == "__main__":
    cli()
