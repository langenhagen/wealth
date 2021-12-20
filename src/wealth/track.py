"""Functionality to track expenses.
Track expenses and cluster them according to type and subtype."""
from numpy import dtype
import pandas as pd
import pandas.api.types as ptypes
from IPython.core.display import display
from IPython.display import Markdown
from ipywidgets import Output

from wealth.importers.common import to_lower
from wealth.plot import display_df
from wealth.util.util import money_fmt


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
    monthly_end_balances_style = monthly_end_balances.style.format(
        formatter=money_fmt(), na_rep=""
    )

    df.drop("year and month", axis=1, inplace=True)
    df.set_index("date", drop=True, inplace=True)
    n_days = (df.index[0] - df.index[-1]).days
    df.index = df.index.strftime("%Y-%m-%d")
    df_style = df.style.format(
        formatter={
            "price": money_fmt(),
            "monthly shopping balance": money_fmt(),
            "continuous shopping balance": money_fmt(),
            "monthly wealth balance": money_fmt(),
            "continuous wealth balance": money_fmt(),
        },
        na_rep="",
    )

    average_monthly_end_balances = monthly_end_balances.mean().to_frame(name="amount")
    average_monthly_end_balances_style = average_monthly_end_balances.style.format(
        formatter=money_fmt(),
        na_rep="",
    )

    sums_per_type = df.groupby(df["type"])["price"].sum().to_frame()
    sums_per_type.rename(columns={"price": "total expenses"}, inplace=True)
    sums_per_type["avg monthly expenses"] = (
        sums_per_type["total expenses"] / n_days * 30
    )
    sums_per_type_style = sums_per_type.style.format(formatter=money_fmt(), na_rep="")

    out = Output()
    with out:
        display_df(df_style)
        display(Markdown("<br>Average monthly last balances:"))
        display(average_monthly_end_balances_style)
        display(Markdown("<br>Last balances per month:"))
        display(monthly_end_balances_style)
        display(Markdown("<br>Sums per type:"))
        display(sums_per_type_style)

    display(out)

    return df
