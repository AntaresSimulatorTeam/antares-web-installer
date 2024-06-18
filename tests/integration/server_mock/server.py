"""
Simulate a basic web server for testing purposes.

It provides a simple FastAPI server that can be used to test the functionality of the installer.

This server will only run 10 seconds, so it is not suitable for long tests.
"""

import argparse

import uvicorn

from tests.integration.server_mock.web import app

# Define the server configuration
HOST = "127.0.0.1"
PORT = 8080
VERSION = "2.14.0"


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Mock server for testing purposes.")
    parser.add_argument("--version", action="version", version=VERSION)
    parser.parse_args()

    # Create the FastAPI app and start the server
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
