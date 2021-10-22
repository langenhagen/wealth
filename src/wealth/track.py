"""Functionality to track expenses."""
# Track expenses and cluster them according to type and subtype
import pandas as pd
import pandas.api.types as ptypes
from IPython.core.display import display

from wealth.importers.common import to_lower


def init() -> pd.DataFrame:
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

    df["year_and_month"] = df["date"].astype(str).apply(lambda x: x[:7])
    df["monthly_shopping_cumsum"] = (
        df[df["bucket"] == "shopping"].groupby(df["year_and_month"])["price"].cumsum()
    )
    df["monthly_shopping_cumsum"] = df["monthly_shopping_cumsum"].fillna("")
    df["continuous_shopping_cumsum"] = df[df["bucket"] == "shopping"]["price"].cumsum()
    df["continuous_shopping_cumsum"] = df["continuous_shopping_cumsum"].fillna("")

    df["monthly_wealth_cumsum"] = (
        df[df["bucket"] == "wealth"].groupby(df["year_and_month"])["price"].cumsum()
    )
    df["monthly_wealth_cumsum"] = df["monthly_wealth_cumsum"].fillna("")
    df["continuous_wealth_cumsum"] = df[df["bucket"] == "wealth"]["price"].cumsum()
    df["continuous_wealth_cumsum"] = df["continuous_wealth_cumsum"].fillna("")

    df.drop("year_and_month", axis=1, inplace=True)

    df.set_index("date", drop=True, inplace=True)

    display(df)

    sums_per_type = df.groupby(df["type"])["price"].sum().to_frame()

    sums_per_type.rename(columns={"price": "total_expenses"}, inplace=True)
    n_days = (df.index[0] - df.index[-1]).days
    sums_per_type["avg_monthly_expense"] = sums_per_type["total_expenses"] / n_days * 30
    print("Sums per type:\n")
    display(sums_per_type)

    return df
