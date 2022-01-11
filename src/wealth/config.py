"""Contains code to read the yaml-configuration."""
import logging
from copy import deepcopy
from typing import Any, Dict

import dateutil
import yaml

from wealth.util.deepupdate import deepupdate

default = {
    "capital_gains_taxrate": 0.27,
    "currency": "€",
    "inflation_rate": 2,
    "retirement": {
        "birthday": "2000-01-01",
        "retirement_age": 67,
    },
}


def _read_config_yaml() -> Dict[str, Any]:
    """Read the file `config.yml` and write its contents to a dict."""
    filename = "config.yml"
    try:
        with open(f"../config/{filename}", encoding="UTF-8") as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logging.getLogger().warning(f"Could not open {filename}.")
        return {}


def _create_config() -> Dict[str, Any]:
    """Read the file `config.yml` from file and give defaults to values that the
    file doesn't specify."""
    user = _read_config_yaml()
    config_ = deepupdate(default, user)

    retire = config_["retirement"]
    retire["birthday"] = dateutil.parser.parse(retire["birthday"])
    retire["retirement_year"] = retire["birthday"].year + retire["retirement_age"]
    config_["retirement"] = retire

    return config_


config = _create_config()
