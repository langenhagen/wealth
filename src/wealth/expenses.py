"""Functionality to contrast incomes and expenses of `Wealth`."""
import functools
from typing import List

import ipywidgets as widgets
import pandas as pd
from IPython.core.display import display
from IPython.display import Markdown

import wealth
import wealth.util.transaction_type

TransactionType = wealth.util.transaction_type.TransactionType

BoundedIntText = widgets.BoundedIntText
Checkbox = widgets.Checkbox
Dropdown = widgets.Dropdown
HBox = widgets.HBox
Label = widgets.Label
Output = widgets.Output
VBox = widgets.VBox


def _display_expense_dataframes(
    _,
    drp_freq: Dropdown,
    drp_date: Dropdown,
    txt_n_periods: BoundedIntText,
    txt_n_rows: BoundedIntText,
    checkboxes: List[Checkbox],
    chk_show_internal: Checkbox,
    out: Output,
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
            out_df = (
                df[mask]
                .sort_values(by="amount")
                .drop(["date", "year", "month", "day_of_month"], axis=1)
            )
            out_df["amount"] = out_df["amount"].map(wealth.money_fmt())
            wealth.plot.display_dataframe(out_df, txt_n_rows.value)


def biggest_expenses():
    """Display dataframes containing the biggest expenses."""
    out = Output()
    drp_freq = Dropdown(
        description="Frequency:",
        options=wealth.plot.frequency_options,
        value="MS",
        layout=wealth.plot.dropdown_layout,
    )
    drp_date = Dropdown(
        description="Date:", options=[], layout=wealth.plot.dropdown_layout
    )
    txt_n_periods = BoundedIntText(
        1,
        description="Periods:",
        min=1,
        max=10000,
        layout=wealth.plot.text_layout,
    )
    txt_n_rows = BoundedIntText(
        5, description="Rows:", min=1, layout=wealth.plot.text_layout
    )
    checkboxes = []
    chk_show_internal = Checkbox(
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
        VBox(
            [
                HBox([drp_freq, drp_date, txt_n_periods, txt_n_rows]),
                wealth.plot.account_checkboxes(checkboxes),
                chk_show_internal,
            ]
        )
    )
    display(out)
    update_out(None)
