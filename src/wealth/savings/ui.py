"""User Interface related code for savings."""
import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets import HBox, Output

from wealth.ui.display import display
from wealth.ui.format import date_fmt, money_fmt, ratio_fmt, year_fmt
from wealth.ui.plot import setup_yearly_plot_and_axes
from wealth.ui.styles import (
    amount_border,
    balance_border,
    bar_color,
    deposit_border,
    interest_border,
    ratio_border,
    soft_interest_border,
)
from wealth.ui.widgets import create_inflation_widgets, create_interest_widgets

from .logic import savings


class UI:
    """User interface for the savings feature."""

    @staticmethod
    def __plot_account_history(df: pd.DataFrame):
        """Plot given account history dataframe to display its development."""
        cols2colors = {
            "balance": "#550000",
            "net balance": "#880000",
            "net balance after inflation": "#ff0000",
            "deposit cumsum": "#008800",
            "deposit cumsum after inflation": "#00ff00",
        }
        cols = list(cols2colors.keys())

        df = df[["date"] + cols].groupby(["date"]).last()

        for col, color in cols2colors.items():
            plt.plot(df.index, df[col], drawstyle="steps-post", color=color, label=col)

        plt.legend(loc="best", borderaxespad=0.1)

    @staticmethod
    def __display_summary(df: pd.DataFrame):
        """Display the summary dataframe."""
        style = (
            df.style.format(
                formatter={
                    "date": year_fmt,
                    "balance": money_fmt(),
                    "net balance": money_fmt(),
                    "net balance after inflation": money_fmt(),
                    "deposit cumsum": money_fmt(),
                    "deposit cumsum after inflation": money_fmt(),
                    "interest": money_fmt(),
                    "net interest": money_fmt(),
                    "net interest after inflation": money_fmt(),
                    "interest cumsum": money_fmt(),
                    "net interest cumsum": money_fmt(),
                    "net interest cumsum after inflation": money_fmt(),
                    "interest/deposit ratio": ratio_fmt,
                    "net interest/deposit ratio": ratio_fmt,
                }
            )
            .set_properties(subset="balance", **balance_border)
            .set_properties(subset="deposit cumsum", **deposit_border)
            .set_properties(subset="interest", **interest_border)
            .set_properties(subset="interest cumsum", **soft_interest_border)
            .set_properties(subset="interest/deposit ratio", **ratio_border)
            .bar(color=bar_color)
        )
        display(style)

    @staticmethod
    def __display_account_history_df(df: pd.DataFrame):
        """Display the account history DataFrame."""
        style = (
            df.style.bar(color=bar_color)
            .format(
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
                    "net interest cumsum after inflation": money_fmt(),
                    "net balance after inflation": money_fmt(),
                },
                na_rep="",
            )
            .set_properties(subset="amount", **amount_border)
            .set_properties(subset="balance", **balance_border)
            .set_properties(subset="deposit cumsum", **deposit_border)
            .set_properties(subset="interest cumsum", **interest_border)
        )
        display(style)

    def __init__(
        self,
        imported: pd.DataFrame,
        tax_rate: float,
        interest_rate: float,
        inflation_rate: float,
    ):
        """Run the UI callback system."""
        self.__imported = imported
        self.__tax_rate = tax_rate

        self.__txt_interest, hbox_interest = create_interest_widgets(
            interest_rate, max=30
        )
        self.__txt_inflation, hbox_inflation = create_inflation_widgets(
            inflation_rate, max=20
        )
        self.__widgets = HBox([hbox_interest, hbox_inflation])

        self.__out_fig = Output()
        self.__out_summary = Output()
        self.__out_df = Output()

        self.__txt_interest.observe(self.__on_widgets_change, "value")
        self.__txt_inflation.observe(self.__on_widgets_change, "value")

        display(self.__widgets)
        display(self.__out_fig)
        display("# Yearly Summary")
        display(self.__out_summary)

        display("# Account Development")
        display(self.__out_df)

        self.__on_widgets_change()

    def __on_widgets_change(self, *_):
        """On observer change, recalculate the the results, update the
        output."""
        df, summary = savings(
            imported=self.__imported,
            tax_rate=self.__tax_rate,
            interest_rate=self.__txt_interest.value * 0.01,
            inflation_rate=self.__txt_inflation.value * 0.01,
        )
        self.__update_output(df, summary)

        self.df = df
        self.summary = summary

    def __update_output(self, df: pd.DataFrame, summary: pd.DataFrame):
        """Render the output."""
        with self.__out_fig:
            fig = plt.figure(figsize=(10, 7), num="Account Development")
            fig.clear()
            setup_yearly_plot_and_axes(fig, "Account Development")
            UI.__plot_account_history(df)

        self.__out_summary.clear_output()
        with self.__out_summary:
            UI.__display_summary(summary)

        self.__out_df.clear_output()
        with self.__out_df:
            UI.__display_account_history_df(df)
