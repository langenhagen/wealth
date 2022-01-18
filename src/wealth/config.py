"""Contains code to read the yaml-configuration."""
import datetime as dt
import logging
from typing import Any, Dict

import yaml

from wealth.util.deepupdate import deepupdate

default = {
    "capital_gains_taxrate": 0.27,
    "currency": "€",
    "inflation_rate": 0.02,
    "retirement": {
        "birthday": dt.datetime(2000, 1, 1),
        "retirement_age": 67,
    },
}


def __read_config_yaml() -> Dict[str, Any]:
    """Read the file `config.yml` and write its contents to a dict."""
    filename = "config.yml"
    try:
        with open(f"../config/{filename}", encoding="UTF-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.getLogger().warning(f"Could not open {filename}.")
        return {}


def __create_config() -> Dict[str, Any]:
    """Read the file `config.yml` from file and give defaults to values that the
    file doesn't specify."""
    user = __read_config_yaml()
    config_ = deepupdate(default, user)

    retire = config_["retirement"]
    retire["retirement_year"] = retire["birthday"].year + retire["retirement_age"]
    config_["retirement"] = retire

    return config_


config = __create_config()
