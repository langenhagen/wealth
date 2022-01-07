"""Contains general utility functions."""
import wealth.config

date_fmt = "{:%Y-%m-%d}".format
percent_fmt = "{:,.2f}%".format


def money_fmt(currency: str = None):
    """Return a currency string format function with given currency symbol.
    If no currency symbol is given, use the symbol from the config."""
    currency = currency or wealth.config["currency"]
    return ("{:,.2f}" + f"{currency}").format


def Money(value: float, currency: str = None) -> str:
    """Return the given value as a string with given amount and currency symbol.
    If no currency symbol is given, use the symbol from the config."""
    currency = currency or wealth.config["currency"]
    return money_fmt(currency)(value)
