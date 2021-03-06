"""Transaction-related functionality."""
import functools
import ipywidgets as widgets
from IPython.core.display import display
from typing import List

import wealth

Checkbox = widgets.Checkbox
HBox = widgets.HBox
Label = widgets.Label
Output = widgets.Output


def _update_out(_, out: Output, checkboxes: List[Checkbox]):
    """Update the displayed transaction dataframe."""
    df = wealth.df.iloc[::-1]
    out.clear_output()
    accounts = [chk.description for chk in checkboxes if chk.value]
    df = df[df["account"].isin(accounts)].drop(
        ["date", "year", "month", "day_of_month"], axis=1
    )
    df["amount"] = df["amount"].map(wealth.money_fmt())
    with out:
        wealth.plot.display_dataframe(df)
        display(df["amount"].describe())


def transactions():
    """Plot some columns of the dataframe sorted in descending order and allow
    to filter accounts via checkboxes."""
    out = Output()
    checkboxes = []
    update_out = functools.partial(_update_out, checkboxes=checkboxes, out=out)
    wealth.plot.create_account_checkboxes(checkboxes, wealth.df, True, update_out)

    display(wealth.plot.account_checkboxes(checkboxes))
    display(out)

    update_out(None)
