import time

import click


@click.command()
@click.argument("target_dir", type=click.Path())
def install_cli(target_dir):
    """
    Install Antares Web.
    """
    print(f"Starting installation in directory: '{target_dir}'...")
    time.sleep(1)
    print("Installation complete!")
