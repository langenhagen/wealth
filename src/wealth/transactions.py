"""Transaction-related functionality."""
import ipywidgets as widgets
from IPython.core.display import display

import wealth

HBox = widgets.HBox
Label = widgets.Label
Output = widgets.Output


def transactions():
    """Plot some columns of the dataframe sorted in descending order and allow
    to filter accounts via checkboxes."""
    reversed_df = wealth.df.iloc[::-1]
    out = Output()
    checkboxes = []

    def _update_out(_):
        out.clear_output()
        accs = [chk.description for chk in checkboxes if chk.value]
        reversed_df[reversed_df["account"].isin(accs)].drop(
            ["date", "year", "month", "day_of_month"], axis=1, inplace=True
        )
        reversed_df["amount"] = reversed_df["amount"].map(wealth.money_fmt())
        with out:
            wealth.plot.display_dataframe(reversed_df)
            display(wealth.df["amount"].describe())

    wealth.plot.create_account_checkboxes(checkboxes, reversed_df, True, _update_out)
    display(wealth.plot.account_checkboxes(checkboxes))
    display(out)
    _update_out(None)
