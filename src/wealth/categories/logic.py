"""Contains the business logic for the subpackage `categories`."""
from typing import Iterable

import pandas as pd


def categories(imported: pd.DataFrame, regexes: Iterable[str]) -> list[pd.DataFrame]:
    """From the given DataFrame and regexes build category-DataFrames and return
    them."""
    dfs: pd.DataFrame = []
    for regex in regexes:
        rows = imported[imported["all_data"].str.contains(regex)]
        monthly_sums = rows["amount"].resample("M").sum()
        periods2amounts: dict[str, float] = {}
        periods2amounts["monthly"] = monthly_sums

        quarterly_resampler = monthly_sums.resample("Q")
        periods2amounts["quarterly"] = quarterly_resampler.sum()
        periods2amounts["quarterly avg"] = quarterly_resampler.mean()

        yearly_resampler = monthly_sums.resample("A")
        periods2amounts["yearly"] = yearly_resampler.sum()
        periods2amounts["yearly avg"] = yearly_resampler.mean()

        df = pd.DataFrame(data=periods2amounts)
        df.index = df.index.to_period("M")

        dfs.append(df)

    return dfs
