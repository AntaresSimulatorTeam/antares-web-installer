import os
import typing as t


def update_to_2_15(config: t.MutableMapping[str, t.Any]) -> None:
    """
    Update the configuration file to version 2.15 in-place.

    :param config: actual configuration
    """
    nb_cores_min = 1
    nb_cores_max = os.cpu_count() or nb_cores_min
    nb_cores_default = max(nb_cores_min, nb_cores_max - 2)

    # WIP
    if not config:
        config = {}
    # end of WIP

    config.setdefault("launcher", {})
    config["launcher"].setdefault("local", {})
    config["launcher"].setdefault("slurm", {})
    config["launcher"]["local"]["enable_nb_cores_detection"] = True

    # default_n_cpu = config["launcher"]["slurm"].pop("default_n_cpu", None)
    # if default_n_cpu is not None:
    #    nb_cores_default = max(nb_cores_min, min(default_n_cpu, nb_cores_max))

    # config["launcher"]["slurm"]["enable_nb_cores_detection"] = False
    # config["launcher"]["slurm"]["nb_cores"] = {
    #     "min": nb_cores_min,
    #     "default": nb_cores_default,
    #     "max": nb_cores_max,
    # }
