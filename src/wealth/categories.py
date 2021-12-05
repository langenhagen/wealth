"""Functionality to examine expenses via categories."""
import math

import pandas as pd

from wealth.util.util import Money, display_side_by_side


def categories(df: pd.DataFrame, categories: dict[str, str]):
    """Examine all given df's rows that match given categories."""
    dfs = []
    for regex in categories.values():
        rows = df[df["all_data"].str.contains(regex)]
        amount = {}

        monthly = rows["amount"].resample("M").sum()
        amount["monthly"] = monthly

        quarterly = rows["amount"].resample("Q").sum()
        amount["quarterly"] = quarterly
        amount["quarterly avg"] = quarterly / 3

        yearly = rows["amount"].resample("A").sum()
        amount["yearly"] = yearly
        amount["yearly avg"] = yearly / 12

        category_df = pd.DataFrame(amount)
        category_df = category_df.applymap(lambda x: "" if math.isnan(x) else Money(x))
        category_df.index = category_df.index.to_period("M")
        dfs.append(category_df)

    display_side_by_side(dfs, list(categories.keys()))
