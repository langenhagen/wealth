"""Balance-related functionality of `Wealth`."""
import datetime as dt
import functools
from typing import Generator, List

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats
from IPython.core.display import display
from IPython.display import Markdown
from ipywidgets.widgets import (
    BoundedIntText,
    Box,
    Checkbox,
    Dropdown,
    HBox,
    Label,
    Output,
    VBox,
)

import wealth
from wealth.plot import create_account_checkboxes, display_df, style_red_green
from wealth.util.util import money_fmt


def _daterange(start: dt.date, end: dt.date) -> Generator[dt.date, None, None]:
    """Yield dates between, including given start and end dates."""
    for offset in range((end - start).days + 1):
        yield start + dt.timedelta(offset)


def _display_balance(
    _,
    checkboxes: List[Checkbox],
    drp_date: Dropdown,
    out: Output,
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


def balance(df: pd.DataFrame):
    """Show account-related cumulative sum of the dataframe's column `amount` at
    a specified date."""
    out = Output()
    checkboxes = []
    dates = list(_daterange(df.index.date.min(), df.index.date.max()))
    drp_date = Dropdown(
        description="Date: ",
        options=dates,
        value=df.index.date.max(),
        layout=wealth.plot.dropdown_layout,
    )
    update_balance = functools.partial(
        _display_balance,
        checkboxes=checkboxes,
        out=out,
        drp_date=drp_date,
        df=df,
    )
    create_account_checkboxes(checkboxes, df, True, update_balance)
    drp_date.observe(update_balance, "value")

    display(Markdown("# Balance"))
    display(wealth.plot.account_checkboxes(checkboxes))
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
    sum_accs_checkboxes: List[Checkbox],
    single_accs_checkboxes: List[Checkbox],
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
        layout=wealth.plot.dropdown_layout,
    )
    sum_accs_checkboxes, single_accs_checkboxes = [], []

    out = Output()
    with out:
        fig = plt.figure(figsize=(12, 10), num="Cumulative Sum of All Transaction")

    plot = functools.partial(
        _plot_cumsum,
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

    display(Markdown("# Plot"))
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
                    layout=wealth.plot.box_layout,
                ),
            ]
        )
    )
    plot(None)
    display(out)


def _display_mean_and_median(df: pd.DataFrame, caption: str):
    """Display mean, median and display mean and median without outliers."""
    filtered = df.dropna()[np.abs(scipy.stats.zscore(df.dropna())) < 2]

    df_out = pd.DataFrame(
        index=["mean", "median", "filtered mean", "filtered median"],
        data={"values": [df.mean(), df.median(), filtered.mean(), filtered.median()]},
    )
    style = df_out.style.format(formatter=money_fmt(), na_rep="").applymap(
        style_red_green
    )

    out = Output()
    with out:
        display(Markdown(f"### {caption}"))
        display(style)
    return out


def _display_summary(_, txt_n_periods: BoundedIntText, out: Output, df: pd.DataFrame):
    """Display a summary for the given series."""
    n_periods = txt_n_periods.value
    out.clear_output()
    with out:
        display(
            HBox(
                [
                    _display_mean_and_median(df["diff"].tail(n_periods), "Differences"),
                    _display_mean_and_median(
                        df["min diff"].tail(n_periods), "Differences of Minima"
                    ),
                    _display_mean_and_median(
                        df["max diff"].tail(n_periods), "Differences of Maxima"
                    ),
                ]
            )
        )


def _display_mean_balance_dataframes(
    _,
    drp_freq: Dropdown,
    checkboxes: List[Checkbox],
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
    df_out["diff"] = df_out["mean"].diff()
    df_out["min"] = resampler.min()
    df_out["min diff"] = df_out["min"].diff()
    df_out["max"] = resampler.max()
    df_out["max diff"] = df_out["max"].diff()
    df_out.index = df_out.index.strftime("%Y-%m-%d")

    style = (
        df_out.iloc[::-1]
        .style.format(formatter=money_fmt(), na_rep="")
        .applymap(style_red_green)
    )

    with out:
        display_df(style)

        if len(df_out) <= 1:
            return

        inner_out = Output()
        lbl_n_periods = Label("Consider recent Periods:")
        txt_n_periods = BoundedIntText(
            12,
            min=1,
            max=10000,
            layout=wealth.plot.slim_text_layout,
        )
        update_out = functools.partial(
            _display_summary,
            txt_n_periods=txt_n_periods,
            out=inner_out,
            df=df_out,
        )
        txt_n_periods.observe(update_out, "value")
        display(Markdown("## Summary"))
        display(Box([lbl_n_periods, txt_n_periods], layout=wealth.plot.box_layout))
        display(inner_out)
        update_out(None)


def means(df: pd.DataFrame):
    """Display dataframes containing balances for a given frequency."""
    out = Output()
    drp_freq = Dropdown(
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
        df=df,
    )
    drp_freq.observe(update_out, "value")
    create_account_checkboxes(checkboxes, df, True, update_out)

    display(Markdown("# Mean Balances"))
    display(
        VBox(
            [
                HBox([drp_freq], layout=wealth.plot.box_layout),
                wealth.plot.account_checkboxes(checkboxes),
            ]
        )
    )
    display(out)
    update_out(None)
