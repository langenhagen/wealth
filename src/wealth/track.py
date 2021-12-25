"""Functionality to track expenses.
Track expenses and cluster them according to type and subtype."""
import pandas as pd
import pandas.api.types as ptypes
from IPython.core.display import display
from IPython.display import Markdown
from ipywidgets import Output

from wealth.importers.common import to_lower
from wealth.plot import display_df, style_red_fg
from wealth.util.util import money_fmt


def style_track(cols) -> list[str]:
    """Return a green back color if the given value is a budget and return a
    red back color if the given value is an internal transactions."""
    green = "color: #00ff00aa;"
    red = "color: #ff0000aa;"
    wealth = "color: #800080cc;"
    shopping = "color: #ffff00cc;"

    styles = [None] * 9
    styles[4] = shopping if cols["bucket"] == "shopping" else wealth
    if cols["price"] > 0:
        styles[1] = styles[2] = styles[3] = green
    if cols["monthly shopping balance"] < 0:
        styles[5] = red
    if cols["continuous shopping balance"] < 0:
        styles[6] = red
    if cols["monthly wealth balance"] < 0:
        styles[7] = red
    if cols["continuous wealth balance"] < 0:
        styles[8] = red

    return styles


def _import_track_df() -> pd.DataFrame:
    """Import the file `track.csv`."""
    df = pd.read_csv(
        "../csv/track.csv",
        engine="python",
        parse_dates=["date"],
        sep=";",
    )
    return to_lower(df)


def _assert_df_integrity(df: pd.DataFrame):
    """Assert the given track-DataFrame's integrity."""
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


def track() -> pd.DataFrame:
    """Import the file `track.csv` and return it as a DataFrame."""
    df = _import_track_df()
    _assert_df_integrity(df)

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
        .set_index("date", drop=True)
        .rename(
            columns={
                "monthly shopping balance": "shopping",
                "monthly wealth balance": "wealth",
            }
        )
    )
    monthly_end_balances.index = monthly_end_balances.index.to_period("M")
    monthly_end_balances_style = monthly_end_balances.style.format(
        formatter=money_fmt(), na_rep=""
    ).applymap(style_red_fg)

    df.drop("year and month", axis=1, inplace=True)
    df.set_index("date", drop=True, inplace=True)
    n_days = (df.index[-1] - df.index[0]).days
    df.index = df.index.strftime("%Y-%m-%d")
    df.reset_index(inplace=True)
    df_style = df.style.format(
        formatter={
            "price": money_fmt(),
            "monthly shopping balance": money_fmt(),
            "continuous shopping balance": money_fmt(),
            "monthly wealth balance": money_fmt(),
            "continuous wealth balance": money_fmt(),
        },
        na_rep="",
    ).apply(style_track, axis=1)

    numbers_by_bucket = (
        df.groupby(df[df["type"] != "budget"]["bucket"])["price"]
        .sum()
        .mul(-1)
        .to_frame()
        .rename(columns={"price": "total amount"})
    )
    numbers_by_bucket["avg monthly amount"] = (
        numbers_by_bucket["total amount"] / n_days * 30
    )
    numbers_by_bucket["avg last monthly balance"] = monthly_end_balances.mean()
    numbers_by_bucket_style = numbers_by_bucket.style.format(
        formatter=money_fmt(),
        na_rep="",
    ).applymap(style_red_fg)

    numbers_per_type = (
        df.groupby(df["type"])["price"]
        .sum()
        .mul(-1)
        .to_frame()
        .rename(columns={"price": "total amount"})
        .sort_values(by=["total amount"], ascending=False)
    )
    numbers_per_type["avg monthly amount"] = (
        numbers_per_type["total amount"] / n_days * 30
    )
    numbers_per_type_style = numbers_per_type.style.format(
        formatter=money_fmt(), na_rep=""
    )

    out = Output()
    with out:
        display_df(df_style)
        display(Markdown("<br>Numbers per bucket:"))
        display(numbers_by_bucket_style)
        display(Markdown("<br>Numbers per type:"))
        display(numbers_per_type_style)
        display(Markdown("<br>Last balances per month:"))
        display(monthly_end_balances_style)

    display(out)

    return df
