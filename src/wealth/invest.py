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
    capital_raise = "capital raise"

    def __str__(self):
        """Print the enum's value nicely."""
        return self.value

    @staticmethod
    def profit_types() -> tuple[
        "TransactionType", "TransactionType", "TransactionType"
    ]:
        """Return all transaction types that denote incomes."""
        return (
            TransactionType.capital_raise,
            TransactionType.dividend,
            TransactionType.sell,
        )


class Transaction:
    """A singular transaction."""

    def __init__(
        self, date: dt.date, type_: TransactionType, amount: float, shares: int
    ):
        """Initialize the Transaction with the given date stamp as a string of
        type yyy-mm-dd and a transaction amount."""
        self.type_ = type_
        self.date = date
        assert amount > 0, "Amount must be > 0"
        self.amount = amount
        assert shares >= 0, "Shares must be >= 0"
        self.shares = shares

    @staticmethod
    def from_dict(data: dict[str, dict]) -> "Transaction":
        """Create a transaction from a dictionary-representation"""
        keys_ = list(data.keys())
        assert len(keys_) == 1, "Found more than 1 key in a transaction argument"
        type_ = keys_[0]
        transaction = data[type_]
        return Transaction(
            date=dateutil.parser.parse(str(transaction["date"])).date(),
            type_=TransactionType(type_),
            amount=transaction["amount"],
            shares=transaction.get("shares", 0),
        )


@dataclass
class InvestmentSet:
    """A group of transactions that reflect investments and cashout."""

    company: str
    transactions: list[Transaction]

    def start_date(self) -> dt.date:
        """Returns the date of the first transaction."""
        return min([t.date for t in self.transactions])

    def duration(self) -> int:
        """Denotes the duration of the holding in days, minimum 1 day."""
        min_ = min([t.date for t in self.transactions])
        if self.is_open() is True:
            max_ = dt.date.today()
        else:
            max_ = max([t.date for t in self.transactions])
        delta = max_ - min_
        return delta.days + 1

    def is_open(self) -> bool:
        """Indicates whether all shares belonging to the investment set have
        been sold or not."""
        share_balance = 0
        for transaction in self.transactions:
            if transaction.type_ == TransactionType.buy:
                share_balance += transaction.shares
            elif transaction.type_ == TransactionType.sell:
                share_balance -= transaction.shares

        assert share_balance >= 0, "Cannot sell more shares than bought"
        return bool(share_balance)

    def invested_sum(self) -> float:
        """The absolute total amount of money invested."""
        buy = TransactionType.buy
        return sum([t.amount for t in self.transactions if t.type_ is buy])

    def gross_profit(self) -> float:
        """The amount of gross profit."""
        types = TransactionType.profit_types()
        amount = sum([t.amount for t in self.transactions if t.type_ in types])
        return amount - self.invested_sum()

    def _get_individual_shares_and_prices(self, type_: TransactionType) -> list[float]:
        """Return a list of individual share prices for all transactions with
        the given transaction type in the same order as the items are in the
        member `transactions`."""
        transactions = [t for t in self.transactions if t.type_ == type_]
        prices = []
        for transaction in transactions:
            price = transaction.amount / transaction.shares
            prices.extend([price] * transaction.shares)

        return prices

    def net_profit(self, tax_rate: Optional[float] = None) -> Optional[float]:
        """The amount of profit after capital gains taxes on profits. Use the
        tax rate from the configs if the given tax rate is None."""
        if self.is_open() is True:
            return None
        tax_rate = tax_rate or wealth.config["capital_gains_taxrate"]

        buys = self._get_individual_shares_and_prices(TransactionType.buy)
        sells = self._get_individual_shares_and_prices(TransactionType.sell)
        assert len(buys) == len(sells), "Number of bought and sold shares must be equal"

        profit = 0.0
        for buy, sell in zip(buys, sells):

            amount = sell - buy
            if amount > 0:
                profit += amount * (1 - tax_rate)
            else:
                profit += amount

        types = (TransactionType.capital_raise, TransactionType.dividend)
        transactions = [t.amount for t in self.transactions if t.type_ in types]
        profit += sum(transactions) * (1 - tax_rate)

        return profit

    def net_performance(self) -> Optional[float]:
        """Returns the net performance in percent if the investment set is not
        open anymore."""
        sum_ = self.invested_sum()
        if (net_profit := self.net_profit()) is None:
            return None
        return ((sum_ + net_profit) / sum_ - 1) * 100

    def net_performance_per_day(self) -> Optional[float]:
        """Returns the net performance in percent divided by the number of
        days."""
        performance = self.net_performance()
        return None if performance is None else performance / self.duration()


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
        for detail in details:
            transactions.append(Transaction.from_dict(detail))

        investments.append(InvestmentSet(company, transactions))

    return investments


def _summarize_closed_investments(investments: list[InvestmentSet]) -> pd.DataFrame:
    """Convert the given investment sets to a df that contains a summary of each
    closed investment set."""

    past_investments = [i for i in investments if not i.is_open()]
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

    past_investments = [i for i in investments if i.is_open()]
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

    done_investments = [i for i in investments if i.is_open() is False]
    print(f"I made {len(done_investments)} done investments.")

    profits = sum([i.net_profit() for i in done_investments])
    print(f"The net profits are {Money(profits)}.")

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
