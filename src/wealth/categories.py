"""Functionality to examine expenses via categories."""
import math

import pandas as pd

from wealth.ui.display import display_side_by_side
from wealth.ui.format import money_fmt


def categories(df: pd.DataFrame, categories: dict[str, str]):
    """Examine all given df's rows that match given categories.
    Display a dataframe per each given category with monthly sums,
    quarterly sums and averages and yearly sums and averages.
    Extrapolate average values to full quarters or years."""
    df["date"] = pd.to_datetime(df["date"])
    df = df.reset_index(drop=True).set_index("date")
    dfs = []
    for key, regex in categories.items():
        rows = df[df["all_data"].str.contains(regex)]
        amount = {}

        monthly = rows["amount"].resample("M").sum()
        amount["monthly"] = monthly

        quarterly_resampler = monthly.resample("Q")
        amount["quarterly"] = quarterly_resampler.sum()
        amount["quarterly avg"] = quarterly_resampler.mean()

        yearly_resampler = monthly.resample("A")
        amount["yearly"] = yearly_resampler.sum()
        amount["yearly avg"] = yearly_resampler.mean()

        category_df = pd.DataFrame(amount)
        category_df.index = category_df.index.to_period("M")
        style = category_df.style.format(
            formatter=money_fmt(),
            na_rep="",
        ).set_caption(f"<br><h2>{key}</h2>")
        dfs.append(style)

    display_side_by_side(dfs)
