"""Functionality to calculate compound interest against a track record of
savings."""
from typing import Optional

import pandas as pd

from wealth.config import config

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
    tax_rate = tax_rate or config["capital_gains_taxrate"]
    inflation_rate = inflation_rate or config["inflation_rate"]

    imported = import_csv(filename)
    df = build_account_history(
        imported,
        interest_rate=interest_rate,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
    )

    return df
