"""Investment related functionality."""
from typing import Set, Optional, Tuple

import pandas as pd
from IPython.core.display import display
from IPython.display import Markdown

import wealth.inflation


def summary(investments: Set[Tuple[str, float, int, str]]):
    """Summarize the given set investments."""
    sum_all_investments = sum([i[1] for i in investments])
    print(f"Sum all investments: {wealth.Money(sum_all_investments)}\n")

    display(Markdown("## Sums per Stock"))
    stocks = sorted(set(i[3] for i in investments))
    sums = []
    shares = []
    for stock in stocks:
        sum_investments = sum([i[1] for i in investments if i[3] == stock])
        sums.append(sum_investments)
        sum_shares = sum([i[2] for i in investments if i[3] == stock])
        shares.append(sum_shares)

    df = pd.DataFrame({"stock": stocks, "sums": sums, "shares": shares})
    df["sums"] = df["sums"].map(wealth.money_fmt())

    display(df)


def bailout(
    investment_year: int,
    investment: float,
    target_value_rate: float,
    inflation_rate: Optional[float] = None,
    tax_rate: Optional[float] = None,
):
    """List a dataframe with years and amounts that make sense when to bail out.

    You want to bail out when you, after inflation and taxes, get
    `target_value_rate`, e.g. 1.1. for 10% effective gain."""
    years = []
    bailout_values = []
    gross_gains = []
    net_gains = []

    inflation_rate = inflation_rate or wealth.config["inflation_rate"]
    tax_rate = tax_rate or wealth.config["capital_gains_taxrate"]

    for year in range(investment_year, investment_year + 10):
        inflated_value = wealth.inflation.calc_inflated_value(
            investment, investment_year, year, inflation_rate
        )
        gross_gain = (inflated_value * target_value_rate - investment) * (1 + tax_rate)
        bailout_amount = investment + gross_gain

        years.append(year)
        bailout_values.append(bailout_amount)
        gross_gains.append(gross_gain)
        net_gain = inflated_value * target_value_rate - investment
        net_gains.append(net_gain)

    df = pd.DataFrame(
        {
            "year": years,
            "bailout_value": bailout_values,
            "gross gain": gross_gains,
            "net gain": net_gains,
        }
    )
    df["bailout_value"] = df["bailout_value"].map(wealth.money_fmt())
    df["gross gain"] = df["gross gain"].map(wealth.money_fmt())
    df["net gain"] = df["net gain"].map(wealth.money_fmt())
    display(df)
