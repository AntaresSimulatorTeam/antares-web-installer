import re

from antares_web_installer.__about__ import __version__


def test_version():
    assert re.fullmatch(r"\d+\.\d+\.\d+", __version__)
