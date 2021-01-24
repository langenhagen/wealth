"""Contains general utility functions."""
import pandas as pd

import wealth.config


def make_lowercase(df: pd.DataFrame) -> pd.DataFrame:
    """Make all cells in a given DataFrame"s column of type "object" lowercase
    and return the DataFrame."""
    for col in df:
        if df[col].dtype.char == "O":
            df[col] = df[col].str.lower()
    return df


def add_all_data_column(df: pd.DataFrame, delimiter: str = "; ") -> pd.DataFrame:
    """Add a column named "all_data" to the given DataFrame with "all_data"
    being a concatenated string representation of all other columns, separated
    by the given delimiter.
    Return the same object that was passed in."""
    all_data = None
    for col in df:
        if all_data is None:
            all_data = col + ": " + df[col].astype(str)
        else:
            all_data += delimiter + col + ": " + df[col].astype(str)
    df["all_data"] = all_data
    return df


def Money(value: float, currency: str = None) -> str:
    """Return the given value as a string with given amount and currency
    symbol. If no currency symbol is given, use the symbol from the config. If
    the config symbol is also missing, use the sign for euro `€`."""
    if currency is None:
        currency = wealth.config.get("currency", "€")

    return "{:.2f} {}".format(value, currency)
