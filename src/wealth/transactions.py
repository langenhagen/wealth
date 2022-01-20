"""Transaction-related functionality."""
import functools

import pandas as pd
from ipywidgets import Checkbox, Output

from wealth.ui.display import display
from wealth.ui.format import money_fmt
from wealth.ui.styles import green_yellow_bg
from wealth.ui.widgets import align_checkboxes, create_account_checkboxes


def __update_out(_, df: pd.DataFrame, out: Output, checkboxes: list[Checkbox]):
    """Update the displayed transaction dataframe."""
    accounts = [chk.description for chk in checkboxes if chk.value][1:]
    df_out = df[df["account"].isin(accounts)].iloc[::-1]
    out.clear_output()
    style = df_out.style.format(formatter=money_fmt(), subset="amount").apply(
        green_yellow_bg, axis=1
    )

    with out:
        display(style)


def transactions(df: pd.DataFrame):
    """Plot some columns of the dataframe sorted in descending order and allow
    to filter accounts via checkboxes."""
    out = Output()
    checkboxes = []
    update_out = functools.partial(__update_out, df=df, checkboxes=checkboxes, out=out)
    create_account_checkboxes(checkboxes, df, True, update_out)

    display(align_checkboxes(checkboxes))
    display(out)

    update_out(None)
