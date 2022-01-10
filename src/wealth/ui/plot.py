"""Contains generally applicable utility functions for working with the packages
matplotlib and ipyidgets."""
from typing import Callable, List, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
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
    out_checkboxes: List[Checkbox],
    df: pd.DataFrame,
    value: bool,
    callback: Callable,
) -> List[Checkbox]:
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


def account_checkboxes(checkboxes: List[Checkbox]):
    """Return a HBox containing all given account checkboxes."""
    return HBox(
        [Label("Accounts: ", layout=Layout(width="80px")), *checkboxes],
        layout=box,
    )


def create_inflation_widgets(inflation_rate: float) -> Tuple[BoundedFloatText, HBox]:
    """Create a Label, a bounded float text and a slider to adjust inflation,
    initially starting with the given inflation value in percent."""
    label = Label(value="Inflation rate %: ")
    textbox = BoundedFloatText(
        min=0,
        max=100,
        step=0.01,
        value=inflation_rate,
        layout=text_slim,
    )
    slider = FloatSlider(readout=False, min=0, max=100, step=0.01)
    hbox_inflation = HBox([label, textbox, slider])
    jslink((textbox, "value"), (slider, "value"))
    return (textbox, hbox_inflation)


def setup_plot_and_axes(
    fig: mpl.figure.Figure, title: str, xlabel="Time", ylabel="Euros"
):
    """Set up the plot, axes and title for the given figure for a plot."""
    plt.title(title)
    plt.grid(color="k", linestyle="-", linewidth=0.1)
    ax = fig.axes[0]
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%b %d '%y"))
    ax.xaxis.set_major_locator(mpl.dates.MonthLocator())
    ax.xaxis.set_minor_locator(mpl.dates.WeekdayLocator(byweekday=0))
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, _: format(int(x), ","))
    )
    fig.autofmt_xdate()


def setup_yearly_plot_and_axes(
    fig: mpl.figure.Figure, title: str, xlabel="Time", ylabel="Euros"
):
    """Set up the plot, axes and title for the given figure for a plot."""
    plt.title(title)
    plt.grid(color="k", linestyle="-", linewidth=0.1)
    ax = fig.axes[0]
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%Y"))
    ax.xaxis.set_major_locator(mpl.dates.YearLocator())
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, _: format(int(x), ","))
    )
    plt.xticks(rotation=45)
