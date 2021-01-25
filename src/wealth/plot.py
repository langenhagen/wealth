"""Contains generally applicable utility functions for working with the packages
matplotlib and ipyidgets."""
from typing import Callable, List

import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from IPython.core.display import display

checkbox_layout = widgets.Layout(width="100px")
wide_checkbox_layout = widgets.Layout(width="250px")
dropdown_layout = widgets.Layout(width="250px")
text_layout = widgets.Layout(width="150px")
frequency_options = [
    ("Day", "D"),
    ("Week", "W-MON"),
    ("SemiMonth", "SMS"),
    ("Month", "MS"),
    ("Quarter", "QS"),
    ("Year", "AS"),
]
box_layout = widgets.Layout(margin="20px 0px 20px 0px")


def create_account_checkboxes(
    out_checkboxes: List[widgets.Checkbox],
    df: pd.DataFrame,
    value: bool,
    callback: Callable,
) -> List[widgets.Checkbox]:
    """Create checkboxes for every account in the given dataframe, assign the
    given callback to these checkboxes and add them to the given list."""
    chk_all = widgets.Checkbox(
        value=value, description="All", indent=False, layout=checkbox_layout
    )
    out_checkboxes.append(chk_all)
    for account in df["account"].unique():
        chk = widgets.Checkbox(
            value=value, description=account, indent=False, layout=checkbox_layout
        )
        chk.observe(callback, "value")
        widgets.dlink((chk_all, "value"), (chk, "value"))
        out_checkboxes.append(chk)
        out_checkboxes.sort(key=lambda chk: chk.description)
    return out_checkboxes


def display_dataframe(
    df: pd.DataFrame, n_items: int = None, style=None
) -> pd.DataFrame:
    """Plot a dataframe with `max_rows` set to None aka infinity,
    optionally print the DataFrame's head with the given number."""
    with pd.option_context(
        "display.max_rows", None, "display.max_colwidth", None, "display.precision", 2
    ):
        if n_items:
            if style is not None:
                display(
                    df.head(n_items)
                    .style.set_table_styles(style)
                    .background_gradient(cmap="RdYlGn", vmin=-1, vmax=1, axis=0)
                )
            else:
                display(df.head(n_items))
        else:
            if style is not None:
                display(
                    df.style.set_table_styles(style).background_gradient(
                        cmap="RdYlGn", vmin=-1, vmax=1, axis=0
                    )
                )
            else:
                display(df)


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
        mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
    )


def setup_yearly_plot_and_axes(
    fig: mpl.figure.Figure, title: str, xlabel="Time", ylabel="Euros"
):
    """Set up the plot, axes and title for the given figure for a plot."""
    plt.title(title)
    plt.grid(color="k", linestyle="-", linewidth=0.1)
    ax = fig.axes[0]
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.xaxis.set_major_formatter(mpl.dates.DateFormatter("%y"))
    ax.xaxis.set_major_locator(mpl.dates.YearLocator())
    ax.yaxis.set_major_formatter(
        mpl.ticker.FuncFormatter(lambda x, p: format(int(x), ","))
    )
