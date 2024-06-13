"""
This script simulates the behavior of an application and return its current version.
Support script for Windows systems
"""

import sys
import uvicorn


def get_version():
    print("2.14.1")


# entry point
if __name__ == "__main__":
    if "--version" in sys.argv or "-v" in sys.argv:
        get_version()
    elif len(sys.argv) == 1:
        uvicorn.run("server:app", host="127.0.0.1", port=8080, log_level="info")
    else:
        print("Usage: AntaresWebServer [-v | --version]")
