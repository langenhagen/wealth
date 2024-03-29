"""User Interface related code for categories."""
from typing import Iterable

import pandas as pd
from pandas.io.formats.style import Styler

from wealth.ui.display import display_side_by_side
from wealth.ui.format import money_fmt
from wealth.ui.styles import bar_color, monthly_border, quarterly_border, yearly_border

from .logic import categories


def __display_dfs(keys: Iterable[str], dfs: list[pd.DataFrame]) -> None:
    """Display all category DataFrames side-by-side."""

    styles: list[Styler] = []
    for key, df in zip(keys, dfs):
        style = (
            df.style.format(
                formatter=money_fmt(),
                na_rep="",
            )
            .set_properties(subset="monthly", **monthly_border)
            .set_properties(subset="quarterly", **quarterly_border)
            .set_properties(subset="yearly", **yearly_border)
            .set_caption(f"<br><h2>{key}</h2>")
            .bar(color=bar_color, align="zero")
        )
        styles.append(style)

    display_side_by_side(styles)


def ui(df: pd.DataFrame, categories2regexes: dict[str, str]) -> None:
    """Create category-DataFrames and display them side by side."""
    dfs = categories(df, categories2regexes.values())

    __display_dfs(categories2regexes.keys(), dfs)
