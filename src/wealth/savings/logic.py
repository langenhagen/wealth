"""Aggregates the business logic for the subpackage `savings`."""
import pandas as pd

from .account_history import build_account_history, build_summary


def calc_compound_interest(P: float, r: float, t: int, n: int = 1) -> float:
    """Given the initial principal balance P, an interest rate r, the number of
    times interest applied per time period n and the number of time periods
    elapsed t, calculate and return the compound interest."""
    return P * (1 + r / n) ** (t * n)


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
