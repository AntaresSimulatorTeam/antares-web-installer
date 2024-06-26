# Usage

## Command line version(CLI)

Open a new command prompt or powershell instance.
After making sure you are in the directory containing the installer, run the following command:

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
