"""Aggregates the business logic for the subpackage `savings`."""
import pandas as pd

from .account_history import build_account_history, build_summary


def savings(
    imported: pd.DataFrame,
    interest_rate: float,
    tax_rate: float,
    inflation_rate: float,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Build the account history dataframe and the summary return both."""
    df = build_account_history(
        imported,
        interest_rate=interest_rate,
        tax_rate=tax_rate,
        inflation_rate=inflation_rate,
    )
    summary = build_summary(df)

    return df, summary
