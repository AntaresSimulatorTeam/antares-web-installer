import typing as t


def update_for_desktop(config: t.MutableMapping[str, t.Any]) -> None:
    """
    Force desktop_mode to true in config file.

    Remove workspaces other than default workspace.

    :param config: actual configuration
    """
    config["desktop_mode"] = True

    if "storage" not in config:
        raise ValueError("storage missing in config file ", config)
    if "workspaces" not in config["storage"]:
        raise ValueError("workspaces missing in storage config ", config["storage"])
    workspaces = config["storage"]["workspaces"]

    keys_to_remove = [key for key in workspaces if key != "default"]
    for key in keys_to_remove:
        del workspaces[key]
