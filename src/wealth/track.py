"""Functionality to track expenses.
Track expenses and cluster them according to type and subtype."""
import pandas as pd
import pandas.api.types as ptypes
from IPython.core.display import display
from IPython.display import Markdown
from ipywidgets import Output

import wealth
from wealth.importers.common import to_lower
from wealth.plot import display_df


def track() -> pd.DataFrame:
    """Import the file `track.csv` and return it as a DataFrame."""
    df = pd.read_csv(
        "../csv/track.csv",
        engine="python",
        parse_dates=["date"],
        sep=";",
    )

    df = to_lower(df)

    if not ptypes.is_numeric_dtype(df["price"]):
        raise AssertionError(
            "Price column must contain only numeric values. "
            f'Column "price" looks like:\n{df["price"]}'
        )
    if not ptypes.is_datetime64_any_dtype(df["date"]):
        raise AssertionError(
            "Date column must contain only date values. "
            f'Column "date" looks like:\n{df["date"]}'
        )
    if not set(df["bucket"].tolist()) == set(["shopping", "wealth"]):
        raise AssertionError(
            'Bucket column must contain only values "shopping" or "wealth". '
            f'Column "bucket" looks like:\n{set(df["bucket"].tolist())}'
        )
    if not df["date"].is_monotonic:
        raise AssertionError(
            "Date column must be monotonic increasing. "
            f'Column "date" looks like:\n{df["date"]}'
        )

    df["price"] = df["price"] * -1

    df["year and month"] = df["date"].astype(str).apply(lambda x: x[:7])
    df["monthly shopping balance"] = (
        df[df["bucket"] == "shopping"].groupby(df["year and month"])["price"].cumsum()
    )
    df["continuous shopping balance"] = df[df["bucket"] == "shopping"]["price"].cumsum()

    df["monthly wealth balance"] = (
        df[df["bucket"] == "wealth"].groupby(df["year and month"])["price"].cumsum()
    )
    df["continuous wealth balance"] = df[df["bucket"] == "wealth"]["price"].cumsum()

    monthly_end_balances = (
        df[["date", "monthly shopping balance", "monthly wealth balance"]]
        .ffill()
        .groupby(df["year and month"])
        .tail(1)
    )
    monthly_end_balances.set_index("date", drop=True, inplace=True)
    monthly_end_balances.index = monthly_end_balances.index.to_period("M")
    monthly_end_balances.rename(
        columns={
            "monthly shopping balance": "shopping",
            "monthly wealth balance": "wealth",
        },
        inplace=True,
    )
    monthly_end_balances["shopping"] = monthly_end_balances["shopping"].map(
        wealth.money_fmt()
    )
    monthly_end_balances["wealth"] = monthly_end_balances["wealth"].map(
        wealth.money_fmt()
    )

    df.fillna("", inplace=True)
    df.drop("year and month", axis=1, inplace=True)
    df.set_index("date", drop=True, inplace=True)

    sums_per_type = df.groupby(df["type"])["price"].sum().to_frame()
    sums_per_type.rename(columns={"price": "total expenses"}, inplace=True)
    n_days = (df.index[0] - df.index[-1]).days
    sums_per_type["avg monthly expenses"] = (
        sums_per_type["total expenses"] / n_days * 30
    )
    sums_per_type["total expenses"] = sums_per_type["total expenses"].map(
        wealth.money_fmt()
    )
    sums_per_type["avg monthly expenses"] = sums_per_type["avg monthly expenses"].map(
        wealth.money_fmt()
    )

    out = Output()
    with out:
        display_df(df)
        display(Markdown("Last balances per month:"))
        display(monthly_end_balances)
        display(Markdown("Sums per type:\n"))
        display(sums_per_type)

    display(out)

    return df
