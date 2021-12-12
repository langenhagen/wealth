"""Transaction-related functionality."""
import functools
from typing import List

import pandas as pd
from IPython.core.display import display
from ipywidgets import Checkbox, Output

from wealth.plot import account_checkboxes, create_account_checkboxes, display_df
from wealth.util.util import money_fmt


def _update_out(_, df: pd.DataFrame, out: Output, checkboxes: List[Checkbox]):
    """Update the displayed transaction dataframe."""
    df = df.iloc[::-1]
    out.clear_output()
    accounts = [chk.description for chk in checkboxes if chk.value]
    df = df[df["account"].isin(accounts)].drop(
        ["date", "year", "month", "day_of_month"], axis=1
    )
    df["amount"] = df["amount"].map(money_fmt())
    with out:
        display_df(df)


def transactions(df: pd.DataFrame):
    """Plot some columns of the dataframe sorted in descending order and allow
    to filter accounts via checkboxes."""
    out = Output()
    checkboxes = []
    update_out = functools.partial(_update_out, df=df, checkboxes=checkboxes, out=out)
    create_account_checkboxes(checkboxes, df, True, update_out)

    display(account_checkboxes(checkboxes))
    display(out)

    update_out(None)
