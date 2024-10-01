import typing as t


def update_to_2_18(config: t.MutableMapping[str, t.Any]) -> None:
    """
    Update the configuration file to version 2.18 in-place:
    we need to ensure root_path is / and api_prefix is /api
    """
    del config["root_path"]
    config["api_prefix"] = "/api"
