import click
from tests.samples import version


@click.command()
def get_version():
    return version


if __name__ == "__main__":
    get_version()
