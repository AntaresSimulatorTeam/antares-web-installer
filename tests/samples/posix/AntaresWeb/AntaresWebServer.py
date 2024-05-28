"""
This script simulates the behavior of an application and return its current version.
Support script for UNIX system
"""
import click
import uvicorn
from fastapi import FastAPI

# Server part
app = FastAPI()


@app.get("/")
def index():
    return {"response": f"Successfully running"}


# commands part
@click.group()
@click.version_option(version="2.15", message="%(version)s")
def cli():
    pass


@cli.command()
def run():
    """
    Launch Antares web server for testing only.
    """
    uvicorn.run("AntaresWebServer:app", host="127.0.0.1", port=8000, log_level="info")


# entry point
if __name__ == "__main__":
    cli()
