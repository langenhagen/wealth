"""Functionality to display bank transactions."""
import pandas as pd

from wealth.importers import init

from .ui import UI


def transactions() -> pd.DataFrame:
    """Plot the bank transactions sorted in descending order and allow to filter
    accounts via checkboxes."""
    df = init()

    UI(df)

    return df
