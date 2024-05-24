"""
This script simulates the behavior of an application and return its current version.
Support script for Windows systems
"""
import os
import click
import subprocess

from pathlib import Path
from fastapi import FastAPI

ANTARES_VERSION = os.environ.get("ANTARES_VERSION", "2.14")

# Server part
app = FastAPI()


@app.get("/")
def index():
    return {"response": f"Antares web server version : {ANTARES_VERSION}"}


# commands part
@click.group()
@click.version_option(version=ANTARES_VERSION, message="%(version)s")
def cli():
    pass


@cli.command()
def run():
    """
    Launch Antares web server for testing only.
    Must be in background ?
    """
    # test/samples must be replaced by dynamically defined directory
    script_path = Path().resolve().joinpath("tests/samples/nt/AntaresWeb/AntaresWebServer.py")
    subprocess.run(["fastapi", "dev", script_path], shell=True)


# entry point
if __name__ == "__main__":
    cli()
