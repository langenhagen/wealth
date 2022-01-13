"""User Interface related code for savings."""
import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets import Output, VBox

from wealth.ui.display import display
from wealth.ui.format import date_fmt, money_fmt, ratio_fmt
from wealth.ui.plot import setup_yearly_plot_and_axes
from wealth.ui.widgets import create_inflation_widgets, create_interest_widgets


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
            "deposit cumsum after inflation": money_fmt(),
            "interest cumsum": money_fmt(),
            "net interest cumsum": money_fmt(),
            "net balance after inflation": money_fmt(),
        },
        na_rep="",
    )

    display(style)


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


def _plot_account_history(df: pd.DataFrame):
    """Plot given account history dataframe to display its development."""
    cols2colors = {
        "balance": "#0000ff",
        "net balance": "#8888ff",
        "net balance after inflation": "#ff0000",
        "deposit cumsum": "#008800",
        "deposit cumsum after inflation": "#00ff00",
    }
    cols = list(cols2colors.keys())
    colors = list(cols2colors.values())

    df = df[["date"] + cols].groupby(["date"]).last()

    for col, color in cols2colors.items():
        plt.plot(df.index, df[col], drawstyle="steps-post", color=color, label=col)

    plt.legend(loc="best", borderaxespad=0.1)


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

    out_fig = Output()
    with out_fig:
        fig = plt.figure(figsize=(10, 7), num="Account Development")
        fig.clear()
        setup_yearly_plot_and_axes(fig, "Account Development")
        _plot_account_history(df)

    out_df = Output()
    with out_df:
        _display_account_history_df(df)

    display(widgets)
    display("# Summary")
    display(out_summary)

    display("# Account Development")
    display(out_fig)
    display(out_df)

    # TODO write observer
    # TODO wire widgets
