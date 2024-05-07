# Development

This projet uses [Hatch](https://hatch.pypa.io/latest/) to manage the development environment.

## Project setup

➢ To install the [development environment](https://hatch.pypa.io/latest/environment/), run:

```shell
hatch env create
```

> See [hatch env create](https://hatch.pypa.io/latest/cli/reference/#hatch-env-create) documentation

This command will create a virtual environment and install the development dependencies.

> NOTE: `hatch` creates a virtual environment in the `~/.local/share/hatch/env/virtual/antares-web-installer` directory.

➢ To activate the virtual environment, run:

```shell
hatch shell
```

> See [hatch shell](https://hatch.pypa.io/latest/cli/reference/#hatch-shell) documentation

This command will spawn a new shell with the virtual environment activated. Use Ctrl+D to exit the shell.

> NOTE: this command will display the full path to the virtual environment.
> You can use it to configure PyCharm or Visual Studio Code to use this virtual environment.

## Development tasks

➢ To format and lint the source code with [ruff](https://docs.astral.sh/ruff/), run:

```shell
hatch fmt
```

> See [hatch fmt](https://hatch.pypa.io/latest/cli/reference/#hatch-fmt) documentation

➢ To run the tests on the current Python version, run:

```shell
hatch run test
```

> See [hatch run](https://hatch.pypa.io/latest/cli/reference/#hatch-run) documentation

➢ To run the tests on Python 3.12, for example, run:

```shell
hatch run all.py3.12:test
```

➢ To generate the test coverage report, run:

```shell
hatch run cov
```

This command will run the unit tests and generate a coverage report in the `htmlcov` directory.

➢ To check the typing with [mypy](http://mypy-lang.org/), run:

```shell
hatch run types:check
```

## Generating the documentation

➢ To prepare the documentation environment, run:

```shell
hatch env create docs
```

➢ To generate the documentation with [mkdocs](https://www.mkdocs.org/), run:

```shell
hatch run docs:build
```

This command will generate the documentation in the `site` directory.

➢ To serve the documentation locally, run:

```shell
hatch run docs:serve
```

This command will start a local web server to serve the documentation
at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Building the package

➢ To build the package, run:

```shell
hatch build
```

This command will create a `dist` directory with the built package.

➢ To build the package and upload it to [PyPI](https://pypi.org/), run:

```shell
hatch publish
```

➢ To clean the project, run:

```shell
hatch clean
```

This command will remove the `dist` directory.

## Building the binary distribution

➢ To build the binary distribution, run:

```shell
hatch run pyinstaller:build
```

This command will run PyInstaller and generate a standalone executable in the `dist` directory.
