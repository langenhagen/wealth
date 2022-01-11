"""Functionality to calculate compound interest against a track record of
savings."""
from typing import Optional

import pandas as pd

from wealth.config import config
from wealth.ui.display import display
from wealth.ui.format import date_fmt, money_fmt

from .account_history import build_account_history
from .importer import import_csv


def savings(
    filename: str,
    interest_rate: float,
    tax_rate: Optional[float] = None,
    inflation_rate: Optional[float] = None,
) -> pd.DataFrame:
    """Load a savings account history from CSV file, build an account history
    with interest and inflation from it and display the results in an
    interactive manner as a graph and as a table."""
    tax_rate = config["capital_gains_taxrate"] if tax_rate is None else tax_rate
    inflation_rate = (
        config["inflation_rate"] if inflation_rate is None else inflation_rate
    )

    imported = import_csv(filename)
    df = build_account_history(
        imported,
        interest_rate=interest_rate,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
    )

    _display_account_history_df(df)

    return df


def _display_account_history_df(df: pd.DataFrame):
    """Display the account history DataFrame."""
    style = df.style.format(
        formatter={
            "date": date_fmt,
            "amount": money_fmt(),
            "net amount": money_fmt(),
            "net amount after inflation": money_fmt(),
            "balance": money_fmt(),
            "net balance": money_fmt(),
            "deposit cumsum": money_fmt(),
            "interest cumsum": money_fmt(),
            "net interest cumsum": money_fmt(),
            "net balance after inflation": money_fmt(),
        },
        na_rep="",
    )

    display(style)
