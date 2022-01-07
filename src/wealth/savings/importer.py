"""Functionality to import savings-related CSVs."""
import pathlib

import pandas as pd
import pandas.api.types as ptypes

from .type import TransactionType


def _assert_df_integrity(df: pd.DataFrame):
    """Assert the given savings-import-DataFrame's integrity."""
    if not ptypes.is_datetime64_any_dtype(df["date"]):
        raise AssertionError(
            'Column "date" must contain only date values. '
            f'Column "date" looks like:\n{df["date"]}'
        )
    if not df["date"].is_monotonic:
        raise AssertionError(
            'Column "date" must be monotonic increasing. '
            f'Column "date" looks like:\n{df["date"]}'
        )
    if not ptypes.is_numeric_dtype(df["amount"]):
        raise AssertionError(
            'Column "amount" must contain only numeric values. '
            f'Column "amount" looks like:\n{df["amount"]}'
        )


def import_csv(filename: str) -> pd.DataFrame:
    """Import the csv with the given file name as a dataframe."""
    path = pathlib.Path.cwd() / "../csv/" / filename
    df = pd.read_csv(
        path,
        engine="python",
        parse_dates=["date"],
        sep=";",
    )
    _assert_df_integrity(df)

    df["type"] = TransactionType.DEPOSIT

    return df
