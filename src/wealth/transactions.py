"""Transaction-related functionality."""
import functools
from typing import List

import pandas as pd
from ipywidgets import Checkbox, Output

from wealth.plot import (
    account_checkboxes,
    create_account_checkboxes,
    display,
    style_green_yellow_bg,
)
from wealth.util.format import money_fmt


def _update_out(_, df: pd.DataFrame, out: Output, checkboxes: List[Checkbox]):
    """Update the displayed transaction dataframe."""
    accounts = [chk.description for chk in checkboxes if chk.value][1:]
    df_out = df[df["account"].isin(accounts)].iloc[::-1]
    out.clear_output()
    style = df_out.style.format(formatter=money_fmt(), subset="amount").apply(
        style_green_yellow_bg, axis=1
    )

    with out:
        display(style)


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
