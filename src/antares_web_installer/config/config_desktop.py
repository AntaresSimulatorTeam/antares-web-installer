import typing as t


def update_for_desktop(config: t.MutableMapping[str, t.Any]) -> None:
    """
    Force desktop_mode to true in config file.

    :param config: actual configuration
    """
    config["desktop_mode"] = True
