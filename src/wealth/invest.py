"""Investment related functionality."""
import datetime as dt
from dataclasses import dataclass
from enum import Enum
from typing import Optional

import dateutil.parser
import pandas as pd
import yaml

import wealth
from wealth.config import config
from wealth.ui.display import display
from wealth.ui.format import Money, money_fmt, percent_fmt
from wealth.ui.styles import bar_color, red_fg


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

    def end_date(self) -> dt.date:
        """Returns the date of the last transaction."""
        return max([t.date for t in self.transactions])

    def duration(self) -> int:
        """Denotes the duration of the holding in days, minimum 1 day."""
        end_date_ = dt.date.today() if self.is_open() is True else self.end_date()
        delta = end_date_ - self.start_date()
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

    def total_invested_sum(self) -> float:
        """The total amount of money invested."""
        buy = TransactionType.buy
        return sum([t.amount for t in self.transactions if t.type_ is buy])

    def total_returns(self) -> float:
        """The total amount of money returned."""
        types = TransactionType.profit_types()
        return sum([t.amount for t in self.transactions if t.type_ in types])

    def gross_profit(self) -> float:
        """The amount of gross profit."""
        return self.total_returns() - self.total_invested_sum()

    def open_invested_sum(self) -> float:
        """The amount of money still invested - money paid out.
        Can be negative if investments are profitable."""
        return self.total_invested_sum() - self.total_returns()

    def get_individual_shares_and_prices(self, type_: TransactionType) -> list[float]:
        """Return a list of individual share prices for all transactions with
        the given transaction type in the same order as the items are in the
        member `transactions`."""
        transactions = [t for t in self.transactions if t.type_ == type_]
        prices = []
        for t in transactions:
            price_per_share = t.amount / t.shares
            prices.extend([price_per_share] * t.shares)

        return prices

    def net_profit(self, tax_rate: Optional[float] = None) -> Optional[float]:
        """The amount of profit after capital gains taxes on profits. Use the
        tax rate from the configs if the given tax rate is None."""
        tax_rate = config["capital_gains_taxrate"] if tax_rate is None else tax_rate

        gross = self.gross_profit()
        net = gross * (1 - tax_rate) if gross > 0 else gross

        return net

    def net_performance(self) -> Optional[float]:
        """Returns the net performance in percent if the investment set is not
        open anymore."""
        sum_ = self.total_invested_sum()
        if (net_profit := self.net_profit()) is None:
            return None
        return ((sum_ + net_profit) / sum_ - 1) * 100

    def net_performance_per_day(self) -> Optional[float]:
        """Returns the net performance in percent divided by the number of
        days."""
        performance = self.net_performance()
        return None if performance is None else performance / self.duration()


def __load_stocks_yml() -> list[InvestmentSet]:
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


def __summarize_closed_investments(investments: list[InvestmentSet]) -> pd.DataFrame:
    """Convert the given investment sets to a df that contains a summary of each
    closed investment set."""

    past_investments = [i for i in investments if not i.is_open()]
    df = pd.DataFrame(
        {
            "company": [i.company for i in past_investments],
            "start date": [i.start_date() for i in past_investments],
            "end date": [i.end_date() for i in past_investments],
            "days": [i.duration() for i in past_investments],
            "investment": [i.total_invested_sum() for i in past_investments],
            "profit": [i.gross_profit() for i in past_investments],
            "net profit": [i.net_profit() for i in past_investments],
            "net performance": [i.net_performance() for i in past_investments],
            "net daily performance": [
                i.net_performance_per_day() for i in past_investments
            ],
        }
    ).sort_values(by="end date")

    style = (
        df.style.format(
            formatter={
                "investment": money_fmt(),
                "profit": money_fmt(),
                "net profit": money_fmt(),
                "net performance": percent_fmt,
                "net daily performance": percent_fmt,
            },
        )
        .bar(color=bar_color, align="zero")
        .applymap(
            red_fg,
            subset=[
                "profit",
                "net profit",
                "net performance",
                "net daily performance",
            ],
        )
    )

    display(style)


def __summarize_open_investments(investments: list[InvestmentSet]) -> pd.DataFrame:
    """Convert the given investment sets to a df that contains a summary of each
    open investment set."""

    past_investments = [i for i in investments if i.is_open()]
    df = pd.DataFrame(
        {
            "company": [i.company for i in past_investments],
            "start date": [i.start_date() for i in past_investments],
            "days": [i.duration() for i in past_investments],
            "investment": [i.total_invested_sum() for i in past_investments],
        }
    )

    style = df.style.format(formatter={"investment": money_fmt()}).bar(
        color=bar_color,
        align="zero",
    )
    display(style)


def stock(goals: dict[str, int], fulfilled_goals: dict[str, int]):
    """Render information about stock invesments, also in the light of given
    goals and fulfilled goals."""
    display("# Stock Investments")
    investments = __load_stocks_yml()

    done_investments = [i for i in investments if i.is_open() is False]
    open_sum = sum([i.open_invested_sum() for i in investments if i.is_open() is True])
    display(
        f"I currently invest {Money(open_sum)} in "
        f"{len(investments) - len(done_investments)} open investments."
    )
    display(f"I finished {len(done_investments)} investments.")

    if len(done_investments) != 0:
        net_profits = sum([i.net_profit() for i in done_investments])
        display(f"The net profits are {Money(net_profits)}.")

        net_profits_after_goals = net_profits - sum(fulfilled_goals.values())
        display(
            "**The net profits after fulfilled goals are "
            f"{Money(net_profits_after_goals)}.**"
        )

        display(f"The sum of all open goals is {Money(sum(goals.values()))}.")
        display(
            "The sum of all fulfilled goals is "
            f"{Money(sum(fulfilled_goals.values()))}."
        )

    display("<br>Open investments:")
    __summarize_open_investments(investments)

    if len(done_investments) != 0:
        display("<br>Closed investments:")
        __summarize_closed_investments(investments)


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

    inflation_rate = (
        config["inflation_rate"] if inflation_rate is None else inflation_rate
    )
    tax_rate = config["capital_gains_taxrate"] if tax_rate is None else tax_rate

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
            "bailout value": bailout_values,
            "gross gain": gross_gains,
            "net gain": net_gains,
        }
    )

    style = df.style.format(
        subset=[
            "bailout value",
            "gross gain",
            "net gain",
        ],
        formatter=money_fmt(),
    ).bar(subset=["bailout value", "gross gain"], color=bar_color, vmin=0)
    display(style)
