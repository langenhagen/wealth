"""Common ipywidget arrangements."""
from typing import Callable

import pandas as pd
from ipywidgets import (
    BoundedFloatText,
    Checkbox,
    FloatSlider,
    HBox,
    Label,
    Layout,
    dlink,
    jslink,
)

from .layouts import box, checkbox, text_slim

frequency_options = [
    ("Day", "D"),
    ("Week", "W-MON"),
    ("SemiMonth", "SMS"),
    ("Month", "MS"),
    ("Quarter", "QS"),
    ("Year", "AS"),
]


def create_account_checkboxes(
    out_checkboxes: list[Checkbox],
    df: pd.DataFrame,
    value: bool,
    callback: Callable,
) -> list[Checkbox]:
    """Create checkboxes for every account in the given dataframe, assign the
    given callback to these checkboxes and add them to the given list."""
    chk_all = Checkbox(value=value, description="All", indent=False, layout=checkbox)
    out_checkboxes.append(chk_all)
    for account in df["account"].unique():
        chk = Checkbox(value=value, description=account, indent=False, layout=checkbox)
        chk.observe(callback, "value")
        dlink((chk_all, "value"), (chk, "value"))
        out_checkboxes.append(chk)
        out_checkboxes.sort(key=lambda chk: chk.description)
    return out_checkboxes


def align_checkboxes(checkboxes: list[Checkbox]) -> HBox:
    """Return a HBox containing all given checkboxes."""
    return HBox(
        [Label("Accounts: ", layout=Layout(width="80px")), *checkboxes],
        layout=box,
    )


# pylint:disable=redefined-builtin
def create_inflation_widgets(
    inflation_rate: float, max: float
) -> tuple[BoundedFloatText, HBox]:
    """Create a Label, a bounded float text and a slider to adjust inflation,
    initially starting with the given inflation value in percent."""
    label = Label(value="Inflation rate %: ")
    textbox = BoundedFloatText(
        min=0,
        max=max,
        step=0.1,
        value=round(inflation_rate * 100, 1),
        layout=text_slim,
    )
    slider = FloatSlider(readout=False, min=0, max=max, step=0.1)
    hbox = HBox([label, textbox, slider])
    jslink((textbox, "value"), (slider, "value"))
    return (textbox, hbox)


# pylint:disable=redefined-builtin
def create_interest_widgets(
    interest_rate: float, max: float
) -> tuple[BoundedFloatText, HBox]:
    """Create a Label, a bounded float text and a slider to adjust interest rate,
    initially starting with the given inflation value in percent."""
    label = Label(value="Interest rate %: ")
    textbox = BoundedFloatText(
        min=0,
        max=max,
        step=0.1,
        value=round(interest_rate * 100, 1),
        layout=text_slim,
    )
    slider = FloatSlider(readout=False, min=0, max=max, step=0.1)
    hbox = HBox([label, textbox, slider])
    jslink((textbox, "value"), (slider, "value"))
    return (textbox, hbox)
