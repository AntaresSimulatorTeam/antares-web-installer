import typing as t

from antares_web_installer import logger



def update_for_desktop(config: t.MutableMapping[str, t.Any]) -> None:
    """
    Force desktop_mode to true in config file.

    Rmove workspaces other than default workspace.  

    :param config: actual configuration
    """
    config["desktop_mode"] = True

    if "storage" not in config:
        logger.error("storage missing in config file ", config)
        return
    if "workspaces" not in config["storage"]:
        logger.error("storage missing in config file ", config)
        return
    
    workspaces = config["storage"]["workspaces"]

    keys_to_remove = [key for key in workspaces if key != "default"]
    for key in keys_to_remove:
        del workspaces[key]
