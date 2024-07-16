# Antares Web Installer

[![PyPI - Version](https://img.shields.io/pypi/v/antares-study-version.svg)](https://pypi.org/project/antares-study-version)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/antares-study-version.svg)](https://pypi.org/project/antares-study-version)

Python application to install Antares Web Desktop on your local machine.

-----

**Table of Contents**

- [Overview](README.md#overview)
- [Installation](README.md#installation)
- [Usage](README.md#usage)

## Overview

Antares Web Installer allows you to install the Desktop version of Antares Web on your local machine.
The application updates the configuration files, installs an up-to-date version of
the [AntaREST](https://github.com/AntaresSimulatorTeam/AntaREST/releases/latest) server
and [Antares Solver](https://github.com/AntaresSimulatorTeam/Antares_Simulator/releases).
The installer optionally may create a launcher shortcut on the desktop and open the web interface.

The application is available for Windows and Ubuntu in both cli and gui version.


## Installation

Download the latest release on the [installer repository](https://github.com/AntaresSimulatorTeam/antares-web-installer/releases/latest/) depending on your os.


## Usage

### Graphic User Interface (GUI)

Make sure the installer is located in an Antares Web package. 
Double-click on the installer and follow the instructions.

### Command line version (CLI)

Open a new command prompt.

Make sure you are in the directory containing the installer. Run the following command:
```
AntaresWebInstaller[.exe] -s <SOURCE_DIR> -t <TARGET_DIR>
```

If the installer is located in the new Antares Web Desktop directory, run:

```
AntaresWebInstaller[.exe] -t <TARGET_DIR>
```

where `<TARGET_DIR>` is the directory where you want to install the Antares Web Desktop and `<SOURCE_DIR>`
the directory to copy files from. Add `.exe` if you use the installer on Windows.

Note that you can specify an existing directory as value of `TARGET_DIR`, in which case the installer will update the
existing installation.

By default, the installer will generate shortcuts and launch the server at the end of the installation, but you
optionally can decide to deactivate these steps with `--no-shortcut` and `--no-launch`.

Run ```AntaresWebInstaller[.exe] --help``` for more options.
