"""Balance-related functionality of `Wealth`."""
import datetime as dt
import functools
from typing import Generator

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets.widgets import Box, Checkbox, Dropdown, HBox, Label, Output, VBox

from wealth.ui import layouts
from wealth.ui.display import display
from wealth.ui.format import Money, money_fmt
from wealth.ui.plot import setup_plot_and_axes
from wealth.ui.styles import bar_color, conditional_negative_style, css_str_wrap
from wealth.ui.widgets import (
    align_checkboxes,
    create_account_checkboxes,
    frequency_options,
)


def __daterange(start: dt.date, end: dt.date) -> Generator[dt.date, None, None]:
    """Yield dates between, including given start and end dates."""
    for offset in range((end - start).days + 1):
        yield start + dt.timedelta(offset)


def __display_balance(
    _,
    checkboxes: list[Checkbox],
    drp_date: Dropdown,
    out: Output,
    df: pd.DataFrame,
):
    """Plot the balance, i.e. the cumulative sum, of the given dataframe's
    column `amount` at the date of the given dropdown's value."""
    accounts = [c.description for c in checkboxes if c.value and c.description != "All"]
    series = df[df["account"].isin(accounts)]["amount"].resample("D").sum().cumsum()
    date = dt.datetime(drp_date.value.year, drp_date.value.month, drp_date.value.day)
    index = series.index.get_indexer([date.strftime("%Y-%m-%d")], method="pad")[0]

    out.clear_output()

    try:
        value = series.iat[index]
    except KeyError:
        return

    with out:
        display(f'<br><font size="6">{Money(value)}</font>')


def balance(df: pd.DataFrame):
    """Show account-related cumulative sum of the dataframe's column `amount` at
    a specified date."""
    df["date"] = pd.to_datetime(df["date"])
    df = df.reset_index(drop=True).set_index("date")

    out = Output()
    checkboxes: list[Checkbox] = []
    dates = list(__daterange(df.index.date.min(), df.index.date.max()))
    drp_date = Dropdown(
        description="Date: ",
        options=dates,
        value=df.index.date.max(),
        layout=layouts.dropdown,
    )
    update_balance = functools.partial(
        __display_balance,
        checkboxes=checkboxes,
        out=out,
        drp_date=drp_date,
        df=df,
    )
    create_account_checkboxes(checkboxes, df, True, update_balance)
    drp_date.observe(update_balance, "value")

    display("# Balance")
    display(align_checkboxes(checkboxes))
    display(drp_date)
    display(out)
    update_balance(None)


def __create_local_minimum_maximum_df(df: pd.DataFrame) -> pd.DataFrame:
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


def __plot_df(df: pd.DataFrame, freq: str, label: str):
    """Plot given dataframe with the given frequency and label."""
    if freq == "<atomic>":
        plt.step(df.index, df, label=label, where="post")
    elif freq == "<minmax>":
        plt.plot(__create_local_minimum_maximum_df(df), label=label)
    else:
        df = df.rolling(freq).mean()
        plt.plot(df, label=label)


def __plot_cumsum(
    _,
    sum_accs_checkboxes: list[Checkbox],
    single_accs_checkboxes: list[Checkbox],
    out: Output,
    fig: mpl.figure.Figure,
    df: pd.DataFrame,
    drp_freq: Dropdown,
):
    """Plot cumsum graphs with the given params."""
    sum_accs = [chk.description for chk in sum_accs_checkboxes if chk.value]
    single_accounts = [
        chk.description
        for chk in single_accs_checkboxes
        if chk.value and chk.description != "All"
    ]
    show_legend = False
    sum_df = df[df["account"].isin(sum_accs)]
    sum_df.index = sum_df["date"]
    sum_series = sum_df["amount"].cumsum()
    with out:
        fig.clear()
        setup_plot_and_axes(fig, "Cumulative Sum of All transactions")
        if not sum_series.empty:
            __plot_df(sum_series, drp_freq.value, "Combined")
            show_legend = True
        for account in single_accounts:
            single_df = df[df["account"] == account]
            single_df.index = single_df["date"]
            single_series = single_df["amount"].cumsum()
            __plot_df(single_series, drp_freq.value, account)
            show_legend = True
        if show_legend:
            plt.legend(loc="best", borderaxespad=0.1)


def graph(df: pd.DataFrame):
    """Show an account-related cumulative sum graph of the dataframe's column
    `amount`."""
    drp_freq = Dropdown(
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
        layout=layouts.dropdown,
    )
    sum_accs_checkboxes: list[Checkbox] = []
    single_accs_checkboxes: list[Checkbox] = []

    out = Output()
    with out:
        fig = plt.figure(figsize=(12, 10), num="Cumulative Sum of All Transaction")

    plot = functools.partial(
        __plot_cumsum,
        sum_accs_checkboxes=sum_accs_checkboxes,
        single_accs_checkboxes=single_accs_checkboxes,
        out=out,
        fig=fig,
        df=df,
        drp_freq=drp_freq,
    )
    drp_freq.observe(plot, "value")
    create_account_checkboxes(sum_accs_checkboxes, df, True, plot)
    create_account_checkboxes(single_accs_checkboxes, df, True, plot)

    display("# Plot")
    display(
        VBox(
            [
                drp_freq,
                HBox(
                    [
                        VBox(
                            [
                                Label("Accounts for combined plot: "),
                                Label("Accounts for individual plots: "),
                            ]
                        ),
                        VBox(
                            [
                                Box(sum_accs_checkboxes),
                                Box(single_accs_checkboxes),
                            ]
                        ),
                    ],
                    layout=layouts.box,
                ),
            ]
        )
    )
    plot(None)
    display(out)


def __display_mean_balance_dataframes(
    _,
    drp_freq: Dropdown,
    checkboxes: list[Checkbox],
    out: Output,
    df: pd.DataFrame,
):
    """List the balances per timeframes with the given frequency."""
    out.clear_output()
    if df.empty:
        return

    df_out = pd.DataFrame()
    accounts = [c.description for c in checkboxes if c.value and c.description != "All"]
    mask = df["account"].isin(accounts)
    daily_cumsum_df = df[mask]["amount"].resample("D").sum().cumsum()
    resampler = daily_cumsum_df.resample(drp_freq.value)
    df_out["mean"] = resampler.mean()
    df_out["min"] = resampler.min()
    df_out["max"] = resampler.max()

    if df_out.empty:
        return

    df_out.index = df_out.index.strftime("%Y-%m-%d")

    style = (
        df_out.style.format(formatter=money_fmt(), na_rep="")
        .applymap(css_str_wrap(conditional_negative_style))
        .bar(color=bar_color, align="zero")
    )

    with out:
        display(style)


def means(df: pd.DataFrame):
    """Display dataframes containing balances for a given frequency."""
    df["date"] = pd.to_datetime(df["date"])
    df = df.reset_index(drop=True).set_index("date")

    out = Output()
    drp_freq = Dropdown(
        description="Frequency:",
        options=frequency_options,
        value="MS",
        layout=layouts.dropdown,
    )
    checkboxes: list[Checkbox] = []
    update_out = functools.partial(
        __display_mean_balance_dataframes,
        drp_freq=drp_freq,
        checkboxes=checkboxes,
        out=out,
        df=df,
    )
    drp_freq.observe(update_out, "value")
    create_account_checkboxes(checkboxes, df, True, update_out)

    display("# Mean Balances")
    display(
        VBox(
            [
                HBox([drp_freq], layout=layouts.box),
                align_checkboxes(checkboxes),
            ]
        )
    )
    display(out)
    update_out(None)
