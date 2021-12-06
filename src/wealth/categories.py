"""Functionality to examine expenses via categories."""
import math

import pandas as pd

from wealth.util.util import Money, display_side_by_side


def categories(df: pd.DataFrame, categories: dict[str, str]):
    """Examine all given df's rows that match given categories.
    Display a dataframe per each given category with monthly sums,
    quarterly sums and averages and yearly sums and averages.
    Extrapolate average values to full quarters or years."""
    dfs = []
    for regex in categories.values():
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
        category_df = category_df.applymap(lambda x: "" if math.isnan(x) else Money(x))
        category_df.index = category_df.index.to_period("M")
        dfs.append(category_df)

    display_side_by_side(dfs, list(categories.keys()))
