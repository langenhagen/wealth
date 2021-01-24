"""Functionality to contrast incomes and expenses of `Wealth`."""
import functools
from typing import List

import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from IPython.core.display import display
from IPython.display import Markdown

import wealth
import wealth.util.transaction_type

TransactionType = wealth.util.transaction_type.TransactionType


def _get_width(series: pd.Series, freq: str) -> List[int]:
    """Calculate the width of the bars for the according series values."""
    ts = series.index.to_list()
    if not ts:
        return [1]
    ts.append(ts[-1] + pd.tseries.frequencies.to_offset(freq))
    return [(ts[i] - ts[i - 1]).total_seconds() / 86400 for i in range(1, len(ts))]


def _barplot(series: pd.Series, freq: str, label: str):
    """Plot the given series with the given frequency and label as bar plots."""
    style = {"align": "edge", "alpha": 0.5}
    incomes = series[series > 0].resample(freq, label="left", closed="left").sum()
    plt.bar(
        incomes.index,
        incomes,
        label=f"{label} incomes",
        width=_get_width(incomes, freq),
        **style,
    )
    expenses = series[series <= 0].resample(freq, label="left", closed="left").sum()
    plt.bar(
        expenses.index,
        expenses,
        label=f"{label} expenses",
        width=_get_width(expenses, freq),
        **style,
    )


def _plot_incomes_and_expenses(
    _,
    sum_accs_checkboxes: List[widgets.Checkbox],
    single_accs_checkboxes: List[widgets.Checkbox],
    out: widgets.Output,
    fig: mpl.figure.Figure,
    df: pd.DataFrame,
    drp_freq: widgets.Dropdown,
    chk_show_internal: widgets.Checkbox,
):
    """Plot bar plots with the given params."""
    sum_accs = [chk.description for chk in sum_accs_checkboxes if chk.value]
    single_accounts = [
        chk.description
        for chk in single_accs_checkboxes
        if chk.value and chk.description != "All"
    ]
    if chk_show_internal.value is False and not df.empty:
        df = df[
            df["transaction_type"]
            .astype("category")
            .isin([TransactionType.IN, TransactionType.OUT])
        ]
    show_legend = False
    with out:
        fig.clear()
        wealth.plot.setup_plot_and_axes(fig, "Incomes and Expenses")
        if not df.empty:
            sum_series = df[df["account"].isin(sum_accs)].get("amount")
            if not sum_series.empty:
                _barplot(sum_series, drp_freq.value, "combined")
                show_legend = True
            for account in single_accounts:
                single_series = df[df["account"] == account].get("amount")
                if not single_series.empty:
                    _barplot(single_series, drp_freq.value, account)
                    show_legend = True
        if show_legend:
            plt.legend(loc="best", borderaxespad=0.1)
        fig.autofmt_xdate()


def _display_expense_dataframes(
    _,
    drp_freq: widgets.Dropdown,
    drp_date: widgets.Dropdown,
    txt_n_periods: widgets.BoundedIntText,
    txt_n_rows: widgets.BoundedIntText,
    checkboxes: List[widgets.Checkbox],
    chk_show_internal: widgets.Checkbox,
    out: widgets.Output,
    df: pd.DataFrame,
):
    """List the biggest expenses per timeframes with the given frequency."""
    off = pd.tseries.frequencies.to_offset(drp_freq.value)
    if chk_show_internal.value is False and not df.empty:
        df = df[
            df["transaction_type"]
            .astype("category")
            .isin(
                [
                    TransactionType.IN,
                    TransactionType.OUT,
                ]
            )
        ]
    rng = pd.date_range(df.index.min() - off, df.index.max() + off, freq=drp_freq.value)
    fmt = "%a, %Y-%m-%d"
    drp_date.options = rng[0:-1].sort_values(ascending=False).strftime(fmt).to_list()
    rng = rng[rng <= pd.Timestamp(drp_date.value) + off]
    day_off = pd.tseries.frequencies.to_offset("D")
    accounts = [c.description for c in checkboxes if c.value and c.description != "All"]
    out.clear_output()
    if df.empty:
        return
    for i in range(len(rng) - 1, max(len(rng) - 1 - txt_n_periods.value, 0), -1):
        mask = (
            (df.index >= rng[i - 1])
            & (df["date"] < rng[i])
            & (df["account"].isin(accounts))
            & (
                df["transaction_type"]
                .astype("category")
                .isin([TransactionType.INTERNAL_OUT, TransactionType.OUT])
            )
        )
        with out:
            start = rng[i - 1].strftime(fmt)
            end = (rng[i] - day_off).strftime(fmt)
            display(Markdown(f"## {start} – {end}"))
            wealth.plot.display_dataframe(
                df[mask]
                .sort_values(by="amount")
                .drop(["date", "year", "month", "day_of_month"], axis=1),
                txt_n_rows.value,
            )


def expense_dataframes():
    """Display dataframes containing the biggest expenses."""
    out = widgets.Output()
    drp_freq = widgets.Dropdown(
        description="Frequency:",
        options=wealth.plot.frequency_options,
        value="MS",
        layout=wealth.plot.dropdown_layout,
    )
    drp_date = widgets.Dropdown(
        description="Date:", options=[], layout=wealth.plot.dropdown_layout
    )
    txt_n_periods = widgets.BoundedIntText(
        1,
        description="Periods:",
        min=1,
        max=10000,
        layout=wealth.plot.text_layout,
    )
    txt_n_rows = widgets.BoundedIntText(
        5, description="Rows:", min=1, layout=wealth.plot.text_layout
    )
    checkboxes = []
    chk_show_internal = widgets.Checkbox(
        value=True,
        description="Show Internal Transactions",
        indent=False,
        layout=wealth.plot.wide_checkbox_layout,
    )
    update_out = functools.partial(
        _display_expense_dataframes,
        drp_freq=drp_freq,
        drp_date=drp_date,
        txt_n_periods=txt_n_periods,
        txt_n_rows=txt_n_rows,
        checkboxes=checkboxes,
        chk_show_internal=chk_show_internal,
        out=out,
        df=wealth.df,
    )
    drp_freq.observe(update_out, "value")
    drp_date.observe(update_out, "value")
    txt_n_periods.observe(update_out, "value")
    txt_n_rows.observe(update_out, "value")
    wealth.plot.create_account_checkboxes(checkboxes, wealth.df, True, update_out)
    chk_show_internal.observe(update_out, "value")

    display(Markdown("## Biggest Expenses"))
    display(
        widgets.VBox(
            [
                widgets.HBox([drp_freq, drp_date, txt_n_periods, txt_n_rows]),
                widgets.HBox([widgets.Label("Accounts: "), *checkboxes]),
                chk_show_internal,
            ]
        )
    )
    display(out)
    update_out(None)
