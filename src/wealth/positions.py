"""Functionality to inspect regular income and expense posts."""
import functools
from typing import Dict

import ipywidgets as widgets
import matplotlib.pyplot as plt
import pandas as pd
from IPython.core.display import display
from IPython.display import Markdown

import wealth.util.util

Money = wealth.util.util.Money

Positions = Dict[str, float]


def _show_sums(
    _,
    out: widgets.Output,
    expenses_df: pd.DataFrame,
    sums_df: pd.DataFrame,
    txt_multiplier: widgets.BoundedIntText,
):
    """Display the sums of all the Position groups."""
    expenses_df = expenses_df * txt_multiplier.value
    sums_df = sums_df * txt_multiplier.value
    out.clear_output()
    with out, pd.option_context("display.max_rows", None, "display.precision", 2):
        display(Markdown("### Expenses"))
        display(expenses_df)
        display(Markdown("### Buckets"))
        display(sums_df)


def _plot_piechart_of_position_groups(
    sum_fixed_costs: float,
    sum_variable_costs: float,
    sum_safety_costs: float,
    sum_savings: float,
):
    """Plot a pie chart that shows the relations of the expene-related position
    groups."""
    labels = ["fixed_costs", "variable_costs", "safety_costs", "savings"]
    values = [sum_fixed_costs, sum_variable_costs, sum_safety_costs, sum_savings]
    fig = plt.figure(figsize=(8, 8), num="Ratios of Expense Post Groups")
    fig.set_facecolor("white")
    plt.grid()
    plt.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    plt.show()


def sums(
    incomes: Positions,
    fixed_costs: Positions,
    variable_costs: Positions,
    safety_costs: Positions,
    savings: Positions,
):
    """Show the sums of posts and relations of posts."""
    expenses_dict = dict(**fixed_costs, **variable_costs, **safety_costs, **savings)
    expenses_df = pd.DataFrame.from_dict(
        expenses_dict, orient="index", columns=["cost"]
    )

    sum_incomes = sum(incomes.values())
    sum_fixed_costs = sum(fixed_costs.values())
    sum_variable_costs = sum(variable_costs.values())
    sum_safety_costs = sum(safety_costs.values())
    sum_costs = sum_fixed_costs + sum_variable_costs + sum_safety_costs
    sum_savings = sum(savings.values())
    rest = sum_incomes - sum_costs - sum_savings
    txt_multiplier = widgets.BoundedIntText(
        value=1,
        min=1,
        max=9990,
        description="Multiplier:",
    )
    out = widgets.Output()

    sums_df = pd.DataFrame(
        {
            "cost": [
                sum_incomes,
                sum_fixed_costs,
                sum_variable_costs,
                sum_safety_costs,
                sum_costs,
                sum_savings,
                rest,
            ]
        },
        index=[
            "incomes",
            "fixed costs",
            "variable costs",
            "safety costs",
            "all costs",
            "savings",
            "rest",
        ],
    )
    show_sums = functools.partial(
        _show_sums,
        out=out,
        expenses_df=expenses_df,
        sums_df=sums_df,
        txt_multiplier=txt_multiplier,
    )
    txt_multiplier.observe(show_sums, "value")

    display(Markdown("## Sums of Positions"))
    display(txt_multiplier)
    display(out)
    show_sums(None)
    display(Markdown("## Rations of Expenses"))
    _plot_piechart_of_position_groups(
        sum_fixed_costs=sum_fixed_costs,
        sum_variable_costs=sum_variable_costs,
        sum_safety_costs=sum_safety_costs,
        sum_savings=sum_savings,
    )


def expenses(
    fixed_costs: Positions,
    variable_costs: Positions,
    safety_costs: Positions,
    savings: Positions,
):
    """Plot a pie chart that shows the relations of all expense positions."""
    all_expenses = dict(**fixed_costs, **variable_costs, **safety_costs, **savings)
    fig = plt.figure(figsize=(10, 10), num="Ratios of Expense Posts")
    fig.set_facecolor("white")
    plt.grid()
    plt.pie(
        all_expenses.values(),
        labels=all_expenses.keys(),
        autopct="%1.1f%%",
        startangle=90,
    )
    plt.show()
