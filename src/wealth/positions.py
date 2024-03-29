"""Functionality to inspect regular income and expense postitions."""
import functools
import operator

import matplotlib.pyplot as plt
import pandas as pd
from ipywidgets import BoundedIntText, Output

from wealth.ui import layouts
from wealth.ui.display import display
from wealth.ui.format import money_fmt, percent_fmt
from wealth.ui.styles import bar_color

Positions = dict[str, dict[str, float]]


def __show_sums(
    _,
    out: Output,
    df: pd.DataFrame,
    sums_df: pd.DataFrame,
    txt_multiplier: BoundedIntText,
) -> None:
    """Display the sums of all the Position groups."""
    df = df.copy()
    df["cost"] *= txt_multiplier.value
    sums_df = sums_df.copy()
    sums_df["cost"] *= txt_multiplier.value
    out.clear_output()
    with out, pd.option_context("display.max_rows", None, "display.precision", 2):
        display("### Incomes")
        incomes = df.loc[df["cost"] > 0].sort_values(by="cost", ascending=False)
        incomes["percent"] = (incomes["cost"] / incomes["cost"].sum()) * 100
        incomes_style = incomes.style.format(
            formatter={
                "cost": money_fmt(),
                "percent": percent_fmt,
            }
        ).bar(subset="cost", color=bar_color, align="mid")
        display(incomes_style)

        display("### Expenses")
        expenses = df.loc[df["cost"] <= 0].sort_values(by="cost")
        expenses["percent"] = (expenses["cost"] / expenses["cost"].sum()) * 100

        expenses_style = expenses.style.format(
            formatter={
                "cost": money_fmt(),
                "percent": percent_fmt,
            }
        ).bar(subset="cost", color=bar_color, align="mid")
        display(expenses_style)

        display("### Buckets")

        display("#### Incomes")
        income_sums = sums_df.loc[sums_df["cost"] > 0].sort_values(
            by="cost", ascending=False
        )
        income_sums["percent"] = (income_sums["cost"] / income_sums["cost"].sum()) * 100

        income_sums_style = income_sums.style.format(
            formatter={
                "cost": money_fmt(),
                "percent": percent_fmt,
            }
        ).bar(subset="cost", color=bar_color, align="mid")
        display(income_sums_style)

        display("#### Expenses")
        expense_sums = sums_df.loc[sums_df["cost"] <= 0].sort_values(by="cost")
        expense_sums["percent"] = (
            expense_sums["cost"] / expense_sums["cost"].sum()
        ) * 100

        expense_sums_style = expense_sums.style.format(
            formatter={
                "cost": money_fmt(),
                "percent": percent_fmt,
            }
        ).bar(subset="cost", color=bar_color, align="mid")
        display(expense_sums_style)


def __plot_piechart_of_expense_bucket_sums(bucket_sums: dict[str, float]) -> None:
    """Plot a pie chart that shows the relations of expense-related buckets."""
    bucket_sums = dict(filter(lambda item: item[1] < 0, bucket_sums.items()))
    bucket_sum_items = sorted(bucket_sums.items(), key=operator.itemgetter(1))
    labels = [item[0] for item in bucket_sum_items]
    values = [abs(item[1]) for item in bucket_sum_items]
    fig = plt.figure(figsize=(8, 8), num="Ratios of Expense Post Groups")
    fig.set_facecolor("white")
    plt.grid()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.show()


def __plot_piechart_of_expense_positons(posts: dict[str, float]) -> None:
    """Plot a pie chart that shows the relations of expense-positions."""
    posts = dict(filter(lambda item: item[1] < 0, posts.items()))
    post_items = sorted(posts.items(), key=operator.itemgetter(1))
    labels = [item[0] for item in post_items]
    values = [abs(item[1]) for item in post_items]
    fig = plt.figure(figsize=(10, 10), num="Ratios of Expense Posts")
    fig.set_facecolor("white")
    plt.grid()
    plt.pie(values, labels=labels, autopct="%1.1f%%")
    plt.show()


def positions(buckets: Positions) -> None:
    """Show the sums of positions and relations of positions."""
    bucket_sums = {}
    posts = {}
    for bucket_name, bucket in buckets.items():
        bucket_sums[bucket_name] = sum(bucket.values())
        for post, value in bucket.items():
            posts[post] = (value, bucket_name)

    bucket_sums["rest"] = sum([v[0] for v in posts.values()])
    posts["rest"] = (sum([v[0] for v in posts.values()]), "")
    df = pd.DataFrame.from_dict(posts, orient="index", columns=["cost", "bucket"])

    sums_df = pd.DataFrame(
        {"cost": list(bucket_sums.values())}, index=list(bucket_sums.keys())
    )

    txt_multiplier = BoundedIntText(
        value=1,
        min=1,
        max=9999,
        description="Multiplier:",
        layout=layouts.text,
    )

    out = Output()
    show_sums = functools.partial(
        __show_sums,
        out=out,
        df=df,
        sums_df=sums_df,
        txt_multiplier=txt_multiplier,
    )
    txt_multiplier.observe(show_sums, "value")

    display("## Sums of Positions")
    display(txt_multiplier)
    display(out)
    show_sums(None)
    display("## Ratios of Expenses")
    __plot_piechart_of_expense_bucket_sums(bucket_sums)
    __plot_piechart_of_expense_positons({k: v[0] for k, v in posts.items()})
