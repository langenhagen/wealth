"""Functionality to calculate compound interest against a track record of
savings."""
from typing import Optional

import pandas as pd

from wealth.config import config

from .account_history import build_account_history, build_summary
from .importer import import_csv
from .ui import render


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

    summary = build_summary(df)
    render(
        df=df,
        summary=summary,
        interest_rate=interest_rate,
        inflation_rate=inflation_rate,
    )

    return df
