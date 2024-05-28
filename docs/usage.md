# Usage

## Command line version (CLI)

Open a new terminal and run the following command:

```shell
AntaresWebInstallerCli.exe <TARGET_DIR>
```

where `<TARGET_DIR>` is the directory where you want to install the Antares Web Desktop.

Note that you can specify an existing directory, in which case the installer will update the existing installation.

You optionally can decide whether to create shortcuts on desktop during installation with '-s' and launch server at the 
end of the installation with '-l'. 

Get all options with `--help` :
```shell
python ..\tests\results\nt\AntaresWeb\AntaresWebServer.py --help
```

## Graphical version (GUI)

Double-click on the `AntaresWebInstallerGUI.exe` file and follow the instructions.
