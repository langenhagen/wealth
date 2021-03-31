"""Investment related functionality."""
import pandas as pd
from IPython.core.display import display

import wealth.inflation


def bailout(
    investment_year: int,
    investment: float,
    inflation_rate: float,
    tax_rate: float,
    target_value_rate: float,
):
    """List a dataframe with years and amounts that make sense when to bail out.

    You want to bail out when you, after inflation and taxes, get
    `target_value_rate`, e.g. 1.1. for 10% effective gain."""

    years = []
    bailout_values = []
    gross_gains = []
    net_gains = []

    for year in range(investment_year, investment_year + 10):
        inflated_value = wealth.inflation.calc_inflated_value(
            investment, investment_year, year, inflation_rate
        )
        gross_gain = (inflated_value * target_value_rate - investment) * (
            1 + tax_rate / 100
        )
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
