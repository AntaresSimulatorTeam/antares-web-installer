import typing as t


def update_to_2_19(config: t.MutableMapping[str, t.Any]) -> None:
    """
    Update the configuration file to version 2.19 in-place.

    :param config: actual configuration
    """

    config.setdefault("launcher", {})
    if "local" in config["launcher"]:
        config["launcher"]["local"]["local_workspace"] = "./local_workspace"
    # Don't need to create the folder as it will be created at the local_launcher instantiation inside AntaresWeb
