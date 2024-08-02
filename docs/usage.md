# Usage

## Graphic User Interface (GUI)

Make sure the installer is located in an Antares Web package. 
Double-click on the installer and follow the instructions.

## Command line version (CLI)

Open a new command prompt or powershell instance.
Run the following command:

```
AntaresWebInstaller -t <TARGET_DIR>
```

where `<TARGET_DIR>` is the directory where you want to install the Antares Desktop and `<SOURCE_DIR>`
the directory to copy files from.

Note that you can specify an existing directory as value of `TARGET_DIR`, in which case the installer will update the
existing installation.

By default, the installer will generate shortcuts and launch the server at the end of the installation, but you
optionally can decide to deactivate these steps with `--no-shortcut` and `--no-launch`.

Run ```AntaresWebInstaller[.exe] --help``` for more options.
