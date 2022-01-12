"""User Interface related code for savings."""
import pandas as pd
from ipywidgets import Output, VBox

from wealth.ui.display import display
from wealth.ui.format import date_fmt, money_fmt, ratio_fmt
from wealth.ui.widgets import create_inflation_widgets, create_interest_widgets


def _display_summary(df: pd.DataFrame):
    """Display the summary dataframe."""
    style = (
        df.style.format(
            formatter=money_fmt(),
            subset=(
                [
                    "total accumulated amount",
                    "total net accumulated amount",
                    "total net accumulated amount after inflation",
                    "total invested amount",
                    "total interest received",
                    "total net interest received",
                    "last interest amount",
                    "last net interest amount",
                    "last net interest amount after inflation",
                ],
                ["value"],
            ),
        )
        .format(
            formatter="{:,.1f}",
            subset=(["years"], ["value"]),
        )
        .format(
            formatter=ratio_fmt,
            subset=(
                ["interest/deposit ratio", "net interest/deposit ratio"],
                ["value"],
            ),
        )
    )

    display(style)


def _display_account_history_df(df: pd.DataFrame):
    """Display the account history DataFrame."""
    style = df.style.format(
        formatter={
            "date": date_fmt,
            "amount": money_fmt(),
            "net amount": money_fmt(),
            "net amount after inflation": money_fmt(),
            "balance": money_fmt(),
            "net balance": money_fmt(),
            "deposit cumsum": money_fmt(),
            "interest cumsum": money_fmt(),
            "net interest cumsum": money_fmt(),
            "net balance after inflation": money_fmt(),
        },
        na_rep="",
    )

    display(style)


def render(
    df: pd.DataFrame,
    summary: pd.DataFrame,
    interest_rate: float,
    inflation_rate: float,
):
    """Render the savings case including widgets and graph."""

    txt_interest, hbox_interest = create_interest_widgets(interest_rate, max=30)
    txt_inflation, hbox_inflation = create_inflation_widgets(inflation_rate, max=20)
    widgets = VBox([hbox_interest, hbox_inflation])

    out_summary = Output()
    with out_summary:
        _display_summary(summary)

    out_df = Output()
    with out_df:
        _display_account_history_df(df)

    display(widgets)
    display("# Summary")
    display(out_summary)

    display("# Account Development")
    display(out_df)

    # TODO write observer
    # TODO wire widgets
    # TODO graph, maybe in sep file
