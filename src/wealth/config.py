"""Contains code to read the yaml-configuration."""
import logging
from typing import Any, Dict

import dateutil.parser
import yaml


def _read_config_yaml() -> Dict[str, Any]:
    """Read the file `accounts.yml` and write its contents to a dict."""
    filename = "config.yml"
    try:
        with open(f"../config/{filename}") as file:
            config_dict = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logging.getLogger().warning(f"Could not open {filename}.")
        return {}

    birthday_str = config_dict.get("retirement", {}).get("birthday", "2000-01-01")
    birthday = dateutil.parser.parse(birthday_str)
    config_dict.get("retirement", {})["birthday"] = birthday

    return config_dict


config = _read_config_yaml()
