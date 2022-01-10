"""Contains generally applicable utility functions for working with the packages
matplotlib and ipyidgets."""
from typing import Any, Callable, Iterable, List, Tuple

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import Markdown
from IPython.display import display as ipython_display
from IPython.display import display_html
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

from wealth.util.transaction_type import TransactionType

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


def style_red_fg(value) -> str:
    """Return a red font color if the given value is smaller than 0."""
    return "color: #ff0000aa;" if value < 0 else None


def style_red_green_fg(value) -> str:
    """Return a green font color if the given value is greater or equal than 0,
    else return a red font."""
    return "color: #ff0000aa;" if value < 0 else "color: #00ff00aa;"


def style_green_yellow_bg(cols) -> list[str]:
    """Return a green back color if the given value is an income and return a
    yellow back color if the given value is an internal transactions."""
    type_ = cols["transaction_type"]
    if type_ == TransactionType.IN:
        color = "background: #00ff0044"
    elif type_ in [TransactionType.INTERNAL_IN, TransactionType.INTERNAL_OUT]:
        color = "background: #ffff0044"
    else:
        color = ""
    return [color] * len(cols)


def style_red_green_bg(row) -> str:
    """Return a green back color if the given value is greater or equal than 0,
    else return a red back color. Also render every 2nd row with a darker background darker."""
    color = "background: #ff000044;" if row["amount"] <= 0 else "background: #00ff0044;"
    return [color] * len(row)


def display(o: Any):
    """Display an object.
    Print strings as Markdown.
    Print dataframes and styles with `max_rows` set to None aka infinity,
    `max_colwitdth` set to inifinity and numeric precision set to 2."""
    options = {
        "display.max_rows": None,
        "display.max_colwidth": None,
        "display.precision": 2,
    }
    with pd.option_context(*[i for option in list(options.items()) for i in option]):
        if isinstance(o, pd.DataFrame):
            ipython_display(o.style)
        elif isinstance(o, str):
            ipython_display(Markdown(o))
        else:
            ipython_display(o)


# pylint:disable=protected-access
def display_side_by_side(dfs: Iterable[pd.DataFrame]):
    """Display the given dataframes/styles and the given titles side by side in
    an inline manner."""
    html_str = ""
    for df in dfs:
        style = df if isinstance(df, pd.io.formats.style.Styler) else df.style
        style.set_table_attributes("style='display: inline; padding: 10px;'")
        html_str += style._repr_html_()

    display_html(html_str, raw=True)


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
