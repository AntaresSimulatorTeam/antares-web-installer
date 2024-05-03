import click
import time


@click.version_option(version="2.15.0", message="%(version)s")
@click.group()
def cli():
    pass


if __name__ == "__main__":
    cli()
