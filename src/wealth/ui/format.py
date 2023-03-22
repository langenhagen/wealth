"""Contains string-formatting functions and utilities."""
from typing import Optional

from wealth.config import config

weekday_date = "%a, %Y-%m-%d"

date_fmt = "{:%Y-%m-%d}".format
float_fmt = "{:,.1f}".format
percent_fmt = "{:,.2f}%".format
year_fmt = "{:%Y}".format


def money_fmt(currency: Optional[str] = None):
    """Return a currency string format function with given currency symbol.
    If no currency symbol is given, use the symbol from the config."""
    currency = config["currency"] if currency is None else currency
    return ("{:,.2f}" + f"{currency}").format


def Money(value: float, currency: Optional[str] = None) -> str:
    """Return the given value as a string with given amount and currency symbol.
    If no currency symbol is given, use the symbol from the config."""
    currency = config["currency"] if currency is None else currency
    return money_fmt(currency)(value)


def ratio_fmt(value: float) -> str:
    """Return a percent string with the given ratio value."""
    return percent_fmt(value * 100)
