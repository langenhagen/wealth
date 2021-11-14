"""Investment related functionality."""
import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import dateutil.parser
import pandas as pd
import yaml
from IPython.core.display import display
from IPython.display import Markdown

import wealth
from wealth.util import Money


class TransactionType(Enum):
    """Defines types of transactions."""

    buy = "buy"
    sell = "sell"
    dividend = "dividend"

    def __str__(self):
        """Print the enum's value nicely."""
        return self.value


class Transaction:
    """A singular transaction."""

    def __init__(self, date: dt.date, type_: TransactionType, amount: float):
        """Initialize the Transaction with the given date stamp as a string of
        type yyy-mm-dd and a transaction amount."""
        self.date = date
        self.type_ = type_
        self.amount = amount

    @staticmethod
    def from_dict(data: dict[str, dict]) -> "Transaction":
        """Create a transaction from a dictionary-representation"""
        keys_ = list(data.keys())
        assert len(keys_) == 1, "Found more than 1 key in a transaction argument!"
        type_str = keys_[0]
        transaction = data[type_str]
        amount = transaction["amount"]
        date = dateutil.parser.parse(str(transaction["date"]))
        type_ = TransactionType(type_str)
        return Transaction(date=date, type_=type_, amount=amount)


@dataclass
class InvestmentSet:
    """A group of transactions that reflect investments and cashout."""

    company: str
    transactions: list[Transaction]
    is_open: bool = False  # whether or not positions are still invested

    def start_date(self) -> dt.date:
        """Returns the date of the first transaction."""
        return min([t.date for t in self.transactions])

    def duration(self) -> int:
        """Denotes the duration of the holding in days, minimum 1 day."""
        min_ = min([t.date for t in self.transactions])
        if self.is_open is not True:
            max_ = max([t.date for t in self.transactions])
        else:
            max_ = dt.datetime.today()
        delta = max_ - min_
        return delta.days + 1

    def invested_sum(self) -> float:
        """The absolute total amount of money invested."""
        buy = TransactionType.buy
        return abs(sum([t.amount for t in self.transactions if t.type_ is buy]))

    def gross_profit(self) -> float:
        """The amount of gross profit."""
        dividend, sell = TransactionType.dividend, TransactionType.sell
        amount = sum(
            [t.amount for t in self.transactions if t.type_ in (sell, dividend)]
        )
        return amount - self.invested_sum()

    def net_profit(self, tax_rate: Optional[float] = None) -> float:
        """The amount of profit after capital gains taxes on profits. Use the
        tax rate from the configs if the given tax rate is None."""
        dividend, sell = TransactionType.dividend, TransactionType.sell
        tax_rate = tax_rate or wealth.config["capital_gains_taxrate"]
        amount = sum(
            [t.amount for t in self.transactions if t.type_ in (sell, dividend)]
        )
        profit = amount - self.invested_sum()
        if profit > 0:
            return profit * (1 - tax_rate)
        else:
            return profit

    def net_performance(self) -> float:
        """Returns the net performance in percent."""
        sum_ = self.invested_sum()
        return ((sum_ + self.net_profit()) / sum_ - 1) * 100

    def net_performance_per_day(self) -> float:
        """Returns the net performance in percent divided by the number of
        days."""
        return self.net_performance() / self.duration()


def _load_stocks_yml() -> list[InvestmentSet]:
    """Read the file stocks.yml and return a list of InvestmentSets."""
    with open("../csv/stocks.yml", encoding="UTF-8") as file:
        investment_set_dicts = yaml.safe_load(file)

    investments = []
    for set_ in investment_set_dicts:
        keys_ = list(set_.keys())
        assert len(keys_) == 1, "Found more than 1 company name field"
        company = keys_[0]
        transactions = []
        details = set_[company]
        is_open = False
        for detail in details:
            if detail == "open":
                is_open = True
            else:
                transactions.append(Transaction.from_dict(detail))

        investments.append(InvestmentSet(company, transactions, is_open))

    return investments


def _summarize_closed_investments(investments: list[InvestmentSet]) -> pd.DataFrame:
    """Convert the given investment sets to a df that contains a summary of each
    closed investment set."""

    past_investments = [i for i in investments if not i.is_open]
    past_df = pd.DataFrame(
        {
            "company": [i.company for i in past_investments],
            "start date": [i.start_date() for i in past_investments],
            "days": [i.duration() for i in past_investments],
            "investment": [i.invested_sum() for i in past_investments],
            "profit": [i.gross_profit() for i in past_investments],
            "net profit": [i.net_profit() for i in past_investments],
            "net performance": [i.net_performance() for i in past_investments],
            "net daily performance": [
                i.net_performance_per_day() for i in past_investments
            ],
        }
    )

    past_df["investment"] = past_df["investment"].map(wealth.money_fmt())
    past_df["profit"] = past_df["profit"].map(wealth.money_fmt())
    past_df["net profit"] = past_df["net profit"].map(wealth.money_fmt())
    past_df["net performance"] = past_df["net performance"].map(wealth.percent_fmt)
    past_df["net daily performance"] = past_df["net daily performance"].map(
        wealth.percent_fmt
    )

    display(past_df)


def _summarize_open_investments(investments: list[InvestmentSet]) -> pd.DataFrame:
    """Convert the given investment sets to a df that contains a summary of each
    open investment set."""

    past_investments = [i for i in investments if i.is_open]
    past_df = pd.DataFrame(
        {
            "company": [i.company for i in past_investments],
            "start date": [i.start_date() for i in past_investments],
            "days": [i.duration() for i in past_investments],
            "investment": [i.invested_sum() for i in past_investments],
        }
    )

    past_df["investment"] = past_df["investment"].map(wealth.money_fmt())

    display(past_df)


def stock():
    """Render information about stock invesments."""
    display(Markdown("# Stock Investments"))
    investments = _load_stocks_yml()

    n_investments = len(investments)
    print(f"I made {n_investments} investments.")

    net_profits = sum([i.net_profit() for i in investments if i.is_open is False])
    print(f"The net profits are {Money(net_profits)}.")

    net_perf = sum([i.net_performance() for i in investments if i.is_open is False])
    print(f"The net performance is {wealth.percent_fmt(net_perf)}")

    print("\nClosed investments:")
    _summarize_closed_investments(investments)

    print("\nOpen investments:")
    _summarize_open_investments(investments)


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
