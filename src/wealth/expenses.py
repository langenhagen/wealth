"""Functionality to contrast incomes and expenses of `Wealth`."""
import functools

import pandas as pd
from ipywidgets import BoundedIntText, Checkbox, Dropdown, HBox, Output, VBox

from wealth.ui.display import display
from wealth.ui.format import date_fmt, money_fmt, weekday_date
from wealth.ui.layouts import checkbox_wide, dropdown, dropdown_slim, text
from wealth.ui.styles import bar_color
from wealth.ui.widgets import (
    align_checkboxes,
    create_account_checkboxes,
    frequency_options,
)
from wealth.util.transaction_type import TransactionType


def __display_expense_dataframes(
    _,
    drp_freq: Dropdown,
    drp_date: Dropdown,
    txt_n_periods: BoundedIntText,
    txt_n_rows: BoundedIntText,
    checkboxes: list[Checkbox],
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
    drp_date.options = (
        rng[0:-1].sort_values(ascending=False).strftime(weekday_date).to_list()
    )
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

        df_out = (
            df[mask]
            .sort_values(by="amount")
            .head(txt_n_rows.value)
            .reset_index(drop=True)
        )
        start = rng[i - 1].strftime(weekday_date)
        end = (rng[i] - day_off).strftime(weekday_date)
        style = df_out.style.format(
            formatter={
                "amount": money_fmt(),
                "date": date_fmt,
            }
        ).bar(align="zero", color=bar_color)

        with out:
            display(f"## {start} – {end}")
            display(style)


def biggest_expenses(df: pd.DataFrame):
    """Display dataframes containing the biggest expenses."""
    df.set_index("date", drop=False, inplace=True)
    out = Output()
    drp_freq = Dropdown(
        description="Frequency:",
        options=frequency_options,
        value="MS",
        layout=dropdown_slim,
    )
    drp_date = Dropdown(description="Date:", options=[], layout=dropdown)
    txt_n_periods = BoundedIntText(
        1,
        description="Periods:",
        min=1,
        max=10000,
        layout=text,
    )
    txt_n_rows = BoundedIntText(5, description="Rows:", min=1, layout=text)
    checkboxes: list[Checkbox] = []
    chk_show_internal = Checkbox(
        value=True,
        description="Show Internal Transactions",
        indent=False,
        layout=checkbox_wide,
    )
    update_out = functools.partial(
        __display_expense_dataframes,
        drp_freq=drp_freq,
        drp_date=drp_date,
        txt_n_periods=txt_n_periods,
        txt_n_rows=txt_n_rows,
        checkboxes=checkboxes,
        chk_show_internal=chk_show_internal,
        out=out,
        df=df,
    )
    drp_freq.observe(update_out, "value")
    drp_date.observe(update_out, "value")
    txt_n_periods.observe(update_out, "value")
    txt_n_rows.observe(update_out, "value")
    create_account_checkboxes(checkboxes, df, True, update_out)
    chk_show_internal.observe(update_out, "value")

    display("## Biggest Expenses")
    display(
        VBox(
            [
                HBox([drp_freq, drp_date, txt_n_periods, txt_n_rows]),
                align_checkboxes(checkboxes),
                chk_show_internal,
            ]
        )
    )
    display(out)
    update_out(None)
