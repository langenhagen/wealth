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

    config_dict["inflation_rate"] = config_dict.get("inflation_rate", 2)

    config_dict["retirement"] = retirement = config_dict.get("retirement", {})
    birthday_str = retirement.get("birthday", "2000-01-01")
    birthday = dateutil.parser.parse(birthday_str)
    retirement["birthday"] = birthday

    retirement["retirement_age"] = retirement.get("retirement_age", 67)
    retirement_age = retirement["retirement_age"]
    retirement["retirement_year"] = retirement["birthday"].year + retirement_age

    return config_dict


config = _read_config_yaml()
