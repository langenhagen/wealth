"""Contains code to read the yaml-configuration."""
import logging
from typing import Any, Dict

import dateutil.parser
import yaml


def _read_config_yaml() -> Dict[str, Any]:
    """Read the file `config.yml` and write its contents to a dict.
    Give defaults to values that the file doesn't specify."""
    filename = "config.yml"
    try:
        with open(f"../config/{filename}", encoding="UTF-8") as file:
            config_ = yaml.load(file, Loader=yaml.FullLoader)
    except FileNotFoundError:
        logging.getLogger().warning(f"Could not open {filename}.")
        return {}

    config_["capital_gains_taxrate"] = config_.get("capital_gains_taxrate", 0.27)
    config_["currency"] = config_.get("currency", "€")
    config_["inflation_rate"] = config_.get("inflation_rate", 2)

    config_["retirement"] = retirement = config_.get("retirement", {})
    birthday_str = retirement.get("birthday", "2000-01-01")
    birthday = dateutil.parser.parse(birthday_str)
    retirement["birthday"] = birthday

    retirement["retirement_age"] = retirement.get("retirement_age", 67)
    retirement_age = retirement["retirement_age"]
    retirement["retirement_year"] = retirement["birthday"].year + retirement_age

    return config_


config = _read_config_yaml()
