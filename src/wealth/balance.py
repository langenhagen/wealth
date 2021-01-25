"""Balance-related functionality of `Wealth`."""
import datetime as dt
import functools
from typing import Generator, List

import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
from IPython.core.display import display
from IPython.display import Markdown

import wealth
import wealth.plot


def _daterange(start: dt.date, end: dt.date) -> Generator[dt.date, None, None]:
    """Yield dates between, inclunding, given start and end dates."""
    for offset in range((end - start).days + 1):
        yield start + dt.timedelta(offset)


def _display_balance(
    _,
    checkboxes: List[widgets.Checkbox],
    drp_date: widgets.Dropdown,
    out: widgets.Output,
    df: pd.DataFrame,
):
    """Plot the balance, i.e. the cumulative sum, of the given dataframe's
    column `amount` at the date of the given dropdown's value."""

    accounts = [c.description for c in checkboxes if c.value and c.description != "All"]
    series = df[df["account"].isin(accounts)]["amount"].resample("D").sum().cumsum()
    date = dt.datetime(drp_date.value.year, drp_date.value.month, drp_date.value.day)
    value = series.iloc[series.index.get_loc(date, method="pad")]

    out.clear_output()
    with out:
        display(Markdown(f'<br><font size="6">{wealth.Money(value)}</font>'))


def balance():
    """Show account-related cumulative sum of the dataframe's column `amount` at
    a specified date."""
    out = widgets.Output()
    checkboxes = []
    df = wealth.df
    dates = list(_daterange(df.index.date.min(), df.index.date.max()))
    drp_date = widgets.Dropdown(
        description="Date: ", options=dates, value=df.index.date.max()
    )
    update_balance = functools.partial(
        _display_balance,
        checkboxes=checkboxes,
        out=out,
        drp_date=drp_date,
        df=df,
    )
    wealth.plot.create_account_checkboxes(checkboxes, df, True, update_balance)
    drp_date.observe(update_balance, "value")

    display(Markdown("# Balance"))
    display(
        widgets.Box(
            [widgets.Label("Accounts: "), *checkboxes], layout=wealth.plot.box_layout
        )
    )
    display(drp_date)
    display(out)
    update_balance(None)


def _create_local_minimum_maximum_df(df: pd.DataFrame) -> pd.DataFrame:
    """Create a dataframe consisting of the local minima & maxima of the given
    dataframe as well as its first and last entrees."""
    return pd.concat(
        [
            df.head(1),
            df[
                (df.shift(1) > df) & (df.shift(-1) > df)
                | (df.shift(1) < df) & (df.shift(-1) < df)
            ],
            df.tail(1),
        ]
    )


def _plot_df(df: pd.DataFrame, freq: str, label: str):
    """Plot given dataframe with the given frequency and label."""
    if freq == "<atomic>":
        plt.step(df.index, df, label=label, where="post")
    elif freq == "<minmax>":
        plt.plot(_create_local_minimum_maximum_df(df), label=label)
    else:
        df = df.rolling(freq).mean()
        plt.plot(df, label=label)


def _plot_cumsum(
    _,
    sum_accs_checkboxes: List[widgets.Checkbox],
    single_accs_checkboxes: List[widgets.Checkbox],
    out: widgets.Output,
    fig: mpl.figure.Figure,
    df: pd.DataFrame,
    drp_freq: widgets.Dropdown,
):
    """Plot cumsum graphs with the given params."""
    sum_accs = [chk.description for chk in sum_accs_checkboxes if chk.value]
    single_accounts = [
        chk.description
        for chk in single_accs_checkboxes
        if chk.value and chk.description != "All"
    ]
    show_legend = False
    sum_series = df[df["account"].isin(sum_accs)]["amount"].cumsum()
    with out:
        fig.clear()
        wealth.plot.setup_plot_and_axes(fig, "Cumulative Sum of All transactions")
        if not sum_series.empty:
            _plot_df(sum_series, drp_freq.value, "Combined")
            show_legend = True
        for account in single_accounts:
            single_series = df[df["account"] == account]["amount"].cumsum()
            _plot_df(single_series, drp_freq.value, account)
            show_legend = True
        if show_legend:
            plt.legend(loc="best", borderaxespad=0.1)
        fig.autofmt_xdate()


def cumsum():
    """Show an account-related cumulative sum graph of the dataframe's column
    `amount`."""
    drp_freq = widgets.Dropdown(
        description="Frequency:",
        options=[
            ("Atomic", "<atomic>"),
            ("Minima/Maxima", "<minmax>"),
            ("Day", "D"),
            ("Week", "7D"),
            ("2 Weeks", "14D"),
            ("Month", "30D"),
            ("Quarter", "90D"),
            ("Semester", "180D"),
            ("Year", "365D"),
        ],
        value="<atomic>",
    )
    sum_accs_checkboxes, single_accs_checkboxes = [], []

    out = widgets.Output()
    with out:
        fig = plt.figure(figsize=(12, 10), num="Cumulative Sum of All Transaction")

    plot = functools.partial(
        _plot_cumsum,
        sum_accs_checkboxes=sum_accs_checkboxes,
        single_accs_checkboxes=single_accs_checkboxes,
        out=out,
        fig=fig,
        df=wealth.df,
        drp_freq=drp_freq,
    )
    drp_freq.observe(plot, "value")
    wealth.plot.create_account_checkboxes(sum_accs_checkboxes, wealth.df, True, plot)
    wealth.plot.create_account_checkboxes(single_accs_checkboxes, wealth.df, True, plot)

    display(Markdown("# Plot"))
    display(
        widgets.VBox(
            [
                drp_freq,
                widgets.HBox(
                    [
                        widgets.VBox(
                            [
                                widgets.Label("Accounts for combined plot: "),
                                widgets.Label("Accounts for individual plots: "),
                            ]
                        ),
                        widgets.VBox(
                            [
                                widgets.Box(sum_accs_checkboxes),
                                widgets.Box(single_accs_checkboxes),
                            ]
                        ),
                    ],
                    layout=wealth.plot.box_layout,
                ),
            ]
        )
    )
    plot(None)
    display(out)


def _display_mean_and_median(df: pd.DataFrame):
    """Display mean, median and display mean and median without outliers."""
    filtered = df.dropna()[np.abs(scipy.stats.zscore(df.dropna())) < 2]
    display(
        Markdown(
            '<font size="5">'
            f"Mean: {round(df.mean(), 2)}<br>"
            f"Median: {round(df.median(), 2)}<br>"
            f"Filtered mean: {round(filtered.mean(), 2)}<br>"
            f"Filtered median: {round(filtered.median(), 2)}"
            "</font>"
        )
    )


def _display_mean_balance_dataframes(
    _,
    drp_freq: widgets.Dropdown,
    checkboxes: List[widgets.Checkbox],
    out: widgets.Output,
    df: pd.DataFrame,
):
    """List the balances per timeframes with the given frequency."""
    out.clear_output()
    if df.empty:
        return

    out_df = pd.DataFrame()
    accounts = [c.description for c in checkboxes if c.value and c.description != "All"]
    mask = df["account"].isin(accounts)
    resampler = df[mask]["amount"].resample("D").sum().cumsum().resample(drp_freq.value)
    out_df["mean"] = resampler.mean()
    out_df["diff"] = out_df["mean"].diff()
    out_df["min"] = resampler.min()
    out_df["min_diff"] = out_df["min"].diff()
    out_df["max"] = resampler.max()
    out_df["max_diff"] = out_df["max"].diff()
    out_df.index = out_df.index.strftime("%Y-%m-%d")
    style = [
        dict(selector="th", props=[("font-size", "24px")]),
        dict(selector="td", props=[("font-size", "24px")]),
    ]

    with out:
        wealth.plot.display_dataframe(out_df.iloc[::-1], style=style)

        if len(out_df) <= 1:
            return

        display(Markdown('<br><font size="6">Mean Differences:</font>'))
        _display_mean_and_median(out_df["diff"])
        display(Markdown('<font size="6"><br>Differences of Minima:</font>'))
        _display_mean_and_median(out_df["min_diff"])
        display(Markdown('<font size="6"><br>Differences of Maxima:</font>'))
        _display_mean_and_median(out_df["max_diff"])


def means():
    """Display dataframes containing balances for a given frequency."""
    out = widgets.Output()
    drp_freq = widgets.Dropdown(
        description="Frequency:",
        options=wealth.plot.frequency_options,
        value="MS",
        layout=wealth.plot.dropdown_layout,
    )
    checkboxes = []
    update_out = functools.partial(
        _display_mean_balance_dataframes,
        drp_freq=drp_freq,
        checkboxes=checkboxes,
        out=out,
        df=wealth.df,
    )
    drp_freq.observe(update_out, "value")
    wealth.plot.create_account_checkboxes(checkboxes, wealth.df, True, update_out)

    display(Markdown("# Mean Balances"))
    display(
        widgets.VBox(
            [drp_freq, widgets.HBox([widgets.Label("Accounts: "), *checkboxes])]
        )
    )
    display(out)
    update_out(None)
