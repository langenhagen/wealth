"""Functionality to examine expense bank transactions via categories."""
from wealth.importers import init

from .ui import ui


def categories(categories2regexes: dict[str, str]) -> None:
    """Match all bank transaction DataFrame's rows against given
    categories2regexes.
    Display a dataframe per each given category with monthly sums,
    quarterly sums and averages and yearly sums and averages.
    Extrapolate average values to full quarters or years."""
    df = init().reset_index(drop=True).set_index("date")

    ui(df, categories2regexes)
