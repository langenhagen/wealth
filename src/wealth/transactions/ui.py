"""User Interface related code for transactions."""
import pandas as pd
from ipywidgets import Checkbox, Output

from wealth.ui.display import display
from wealth.ui.format import date_fmt, money_fmt
from wealth.ui.styles import transaction_type_column_styles
from wealth.ui.widgets import align_checkboxes, create_account_checkboxes


class UI:
    """User interface for the transactions feature."""

    def __update_output(self, df: pd.DataFrame):
        """Render the DataFrame."""
        style = df.style.format(
            formatter={
                "amount": money_fmt(),
                "date": date_fmt,
            }
        ).apply(transaction_type_column_styles, axis="columns")

        self.__out.clear_output()
        with self.__out:
            display(style)

    def __on_widgets_change(self, *_):
        """On observer change, recalculate the the results, update the output
        and return the results."""
        accounts = [
            c.description for c in self.__checkboxes if c.value and c.value != "All"
        ]
        df = self.__df[self.__df["account"].isin(accounts)].iloc[::-1]
        self.__update_output(df)

    def __init__(self, df: pd.DataFrame):
        """Run the UI callback system with the given transaction-DataFrame."""
        self.__df = df

        self.__out = Output()
        self.__checkboxes: list[Checkbox] = []
        create_account_checkboxes(self.__checkboxes, df, True, self.__on_widgets_change)

        display(align_checkboxes(self.__checkboxes))
        display(self.__out)

        self.__on_widgets_change()
