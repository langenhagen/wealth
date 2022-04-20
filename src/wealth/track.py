"""Functionality to track expenses.
Track expenses and cluster them according to type and subtype."""
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import pandas.api.types as ptypes
from ipywidgets import Output

from wealth.importers.common import to_lower
from wealth.ui.display import display
from wealth.ui.format import money_fmt
from wealth.ui.styles import (
    bar_color,
    conditional_negative_style,
    conditional_positive_bg_style,
    css_str,
    css_str_wrap,
    monthly_border,
    red_fg,
    shopping_bg,
    shopping_border,
    total_border,
    wealth_bg,
    wealth_border,
)


def __style_track(
    cols,
    special_indices: pd.Index,
    types2colors: dict[str, str],
) -> list[dict[str, str]]:
    """CSS-style the track DataFrame's cells with colors and font weight
    depending on the bucket, type, the balance and whether a row is the last
    entry in a month."""
    styles: list[dict[str, str]] = [{}] * 9

    styles[1] = shopping_bg if cols["bucket"] == "shopping" else wealth_bg

    type_color = types2colors[cols["type"]]
    styles[2] = {"background": type_color, "color": "#000000ee"}.copy()
    styles[3] = {"background": type_color, "color": "#000000ee"}.copy()

    styles[4] = conditional_positive_bg_style(cols["price"])
    if cols["monthly shopping balance"] < 0:
        styles[5] = red_fg.copy()
    if cols["continuous shopping balance"] < 0:
        styles[6] = red_fg.copy()
    if cols["monthly wealth balance"] < 0:
        styles[7] = red_fg.copy()
    if cols["continuous wealth balance"] < 0:
        styles[8] = red_fg.copy()

    if cols.name in special_indices:
        topline = {"border-top": "2px solid #cccccc"}
        for i in range(9):
            styles[i].update(topline.copy())

    return [css_str(s) for s in styles]


def __import_track_df() -> pd.DataFrame:
    """Import the file `track.csv`."""
    df = pd.read_csv(
        "../csv/track.csv",
        engine="python",
        parse_dates=["date"],
        sep=";",
    ).pipe(to_lower)
    df["price"] = df["price"] * -1

    return df[
        [
            "date",
            "bucket",
            "type",
            "what",
            "price",
        ]
    ]


def __assert_df_integrity(df: pd.DataFrame):
    """Assert the given track-DataFrame's integrity."""
    if not ptypes.is_datetime64_any_dtype(df["date"]):
        raise AssertionError(
            'Column "date" must contain only date values. '
            f'Column "date" looks like:\n{df["date"]}'
        )
    if not df["date"].is_monotonic:
        raise AssertionError(
            'Column "date" must be monotonic increasing. '
            f'Column "date" looks like:\n{df["date"]}'
        )
    if not ptypes.is_numeric_dtype(df["price"]):
        raise AssertionError(
            'Column "price" must contain only numeric values. '
            f'Column "price" looks like:\n{df["price"]}'
        )
    if not set(df["bucket"].tolist()) == set(["shopping", "wealth"]):
        raise AssertionError(
            'Column "bucket" must contain only values "shopping" or "wealth". '
            f'Column "bucket" looks like:\n{set(df["bucket"].tolist())}'
        )


def __make_average_month(df: pd.DataFrame) -> pd.DataFrame:
    """Create an average track month dataframe."""

    dfs = []
    for col in ("monthly shopping balance", "monthly wealth balance"):
        c = df[["date", col]].copy()
        c.dropna(inplace=True)

        c["date"] = pd.to_datetime(c["date"])
        c = c.reset_index(drop=True).set_index("date")
        c = c.groupby(c.index).last()

        idx = pd.date_range(c.index.min(), c.index.max())
        c = c.reindex(idx)

        c.fillna(method="pad", inplace=True)
        c = c.groupby(c.index.day).mean()

        dfs.append(c)

    result = pd.concat(dfs, axis="columns")
    return result


def track() -> pd.DataFrame:
    """Import the file `track.csv` and return it as a DataFrame."""
    df = __import_track_df()
    __assert_df_integrity(df)

    n_days = (df["date"].iloc[-1] - df["date"].iloc[0]).days

    year_and_month = df["date"].astype(str).apply(lambda x: x[:7])
    df["monthly shopping balance"] = (
        df[df["bucket"] == "shopping"].groupby(year_and_month)["price"].cumsum()
    )
    df["continuous shopping balance"] = df[df["bucket"] == "shopping"]["price"].cumsum()
    df["monthly wealth balance"] = (
        df[df["bucket"] == "wealth"].groupby(year_and_month)["price"].cumsum()
    )
    df["continuous wealth balance"] = df[df["bucket"] == "wealth"]["price"].cumsum()

    monthly_end_balances = (
        df[["date", "monthly shopping balance", "monthly wealth balance"]]
        .ffill()
        .groupby(year_and_month)
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
    monthly_end_balances_style = (
        monthly_end_balances.style.format(formatter=money_fmt())
        .bar(color=bar_color, align="left", vmin=0)
        .applymap(css_str_wrap(conditional_negative_style))
    )

    monthly_costs = df[df["type"] != "budget"][["date", "bucket"]]
    monthly_costs["shopping"] = -df[df["bucket"] == "shopping"]["price"]
    monthly_costs["wealth"] = -df[df["bucket"] == "wealth"]["price"]
    monthly_costs.fillna(0, inplace=True)
    monthly_costs = monthly_costs.groupby(year_and_month).sum()

    monthly_costs_style = (
        monthly_costs.style.format(formatter=money_fmt())
        .bar(color=bar_color, align="left", vmin=0)
        .applymap(css_str_wrap(conditional_negative_style))
    )

    first_indices_per_month = df.groupby(year_and_month).head(1).index

    types = df["type"].unique()
    types2colors = {}
    cmap = plt.get_cmap("tab20", len(types))
    for type_, i in zip(types, range(cmap.N)):
        hex_ = mpl.colors.rgb2hex(cmap(i))
        types2colors[type_] = hex_

    df["date"] = df["date"].apply(lambda x: x.date())
    style = (
        df.style.format(
            formatter={
                "price": money_fmt(),
                "monthly shopping balance": money_fmt(),
                "continuous shopping balance": money_fmt(),
                "monthly wealth balance": money_fmt(),
                "continuous wealth balance": money_fmt(),
            },
            na_rep="",
        )
        .set_properties(subset="monthly shopping balance", **shopping_border)
        .set_properties(subset="monthly wealth balance", **wealth_border)
        .bar(
            subset=[
                "monthly shopping balance",
                "continuous shopping balance",
                "monthly wealth balance",
                "continuous wealth balance",
            ],
            color=bar_color,
            align="zero",
        )
        .apply(
            __style_track,
            special_indices=first_indices_per_month,
            types2colors=types2colors,
            axis="columns",
        )
    )

    average_month = __make_average_month(df)
    average_month_style = (
        average_month.style.format(formatter=money_fmt())
        .set_properties(subset="monthly shopping balance", **shopping_border)
        .set_properties(subset="monthly wealth balance", **wealth_border)
        .bar(
            subset=[
                "monthly shopping balance",
                "monthly wealth balance",
            ],
            color=bar_color,
            align="zero",
        )
    )

    numbers_by_bucket = (
        df.groupby(df[df["type"] == "budget"]["bucket"])[["bucket", "price"]]
        .sum()
        .rename(columns={"price": "total budget"})
    )
    numbers_by_bucket["total cost"] = (
        df.groupby(df[df["type"] != "budget"]["bucket"])["price"].sum().mul(-1)
    )
    numbers_by_bucket["total balance"] = (
        numbers_by_bucket["total budget"] - numbers_by_bucket["total cost"]
    )
    numbers_by_bucket["avg monthly budget"] = (
        numbers_by_bucket["total budget"] / n_days * 30
    )
    numbers_by_bucket["avg monthly cost"] = (
        numbers_by_bucket["total cost"] / n_days * 30
    )
    numbers_by_bucket["avg monthly end balance"] = (
        numbers_by_bucket["avg monthly budget"] - numbers_by_bucket["avg monthly cost"]
    )

    numbers_by_bucket_style = (
        numbers_by_bucket.style.format(formatter=money_fmt())
        .set_properties(subset="total budget", **total_border)
        .set_properties(subset="avg monthly budget", **monthly_border)
        .applymap(css_str_wrap(conditional_negative_style))
    )

    numbers_per_type = (
        df.groupby(df["type"])["price"]
        .sum()
        .mul(-1)
        .to_frame()
        .rename(columns={"price": "total cost"})
        .sort_values(by=["total cost"], ascending=False)
    )
    numbers_per_type["avg monthly cost"] = numbers_per_type["total cost"] / n_days * 30
    numbers_per_type_style = numbers_per_type.style.format(formatter=money_fmt()).bar(
        align="left",
        color=bar_color,
        subset="total cost",
        vmin=0,
    )

    out = Output()
    with out:
        display(style)
        display("<br>Average month:")
        display(average_month_style)
        display("<br>Numbers per bucket:")
        display(numbers_by_bucket_style)
        display("<br>Numbers per type:")
        display(numbers_per_type_style)
        display("<br>End balances per month:")
        display(monthly_end_balances_style)
        display("<br>Costs per month:")
        display(monthly_costs_style)

    display(out)

    return df
