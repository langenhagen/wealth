"""Defines the package `Wealth`."""
import wealth.balance  # noqa
import wealth.expenses  # noqa
import wealth.importers  # noqa
import wealth.inflation  # noqa
import wealth.interest  # noqa
import wealth.plot  # noqa
import wealth.positions  # noqa
import wealth.transactions  # noqa
from wealth.labels import expense_labels, income_labels  # noqa
from wealth.util.transaction_type import TransactionType  # noqa
from wealth.config import config  # noqa
from wealth.util.util import Money  # noqa

df = wealth.importers.create_dataframe()
