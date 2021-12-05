"""Contains general utility functions."""
import pandas as pd
from IPython.display import display_html

import wealth.config

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


# pylint:disable=protected-access
def display_side_by_side(dfs: list[pd.DataFrame], titles: list[str]):
    """Display the given dataframes and the given titles side by side in an
    inline style."""
    html_str = ""
    for df, title in zip(dfs, titles):
        styler = df.style.set_table_attributes(
            "style='display:inline;padding:10px;'"
        ).set_caption(f"<br><h2>{title}</h2>")
        html_str += styler._repr_html_()

    display_html(html_str, raw=True)
