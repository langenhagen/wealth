"""Contains logic to import sparkasse giro csv files in the csv CAMT format."""
import datetime as dt

import pandas as pd

from wealth.importers.common import add_all_data_column, to_lower, transfer_columns
from wealth.util import TransactionType


def __create_internal_transaction_type(row) -> TransactionType:
    """Create a suitable transaction type according to the given row."""
    return TransactionType.from_row(row, is_internal=True)


def __handle_transactions_between_n26_spaces(df: pd.DataFrame) -> pd.DataFrame:
    """Filter all rows that depict transactions between account-internal
    n26-spaces, rename their account name according to their sub-account and
    double book the according rows for completeness. Screws up the order of
    rows."""
    mask = (pd.isnull(df["iban"])) & (
        df["correspondent"].str.match("from (.+) to (.+)")
    )
    internal = df[mask].copy()
    df = df[~mask]

    spaces = (
        "-" + internal["correspondent"].str.extract("^from (.+) to (.+)")
    ).replace("-main account", "")

    # double booking
    inverted = internal.copy()
    internal.loc[(internal["amount"] > 0), "account"] = internal["account"] + spaces[1]
    internal.loc[(internal["amount"] <= 0), "account"] = internal["account"] + spaces[0]
    internal["transaction_type"] = internal.apply(
        __create_internal_transaction_type, axis="columns"
    )
    inverted.loc[(inverted["amount"] > 0), "account"] = inverted["account"] + spaces[0]
    inverted.loc[(inverted["amount"] <= 0), "account"] = inverted["account"] + spaces[1]
    inverted["amount"] = -inverted["amount"]
    inverted["transaction_type"] = inverted.apply(
        __create_internal_transaction_type, axis="columns"
    )
    df = df.append(internal).append(inverted)
    return df


def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from N26 giro/mastercard accounts and consider n26's
    sub-accounts."""
    df = (
        pd.read_csv(
            path,
            date_parser=lambda x: dt.datetime.strptime(x, "%Y-%m-%d"),
            decimal=".",
            engine="python",
            parse_dates=["Date"],
            sep=",",
            thousands=None,
        )
        .assign(account=account_name, account_type="n26", transaction_type=None)
        .pipe(add_all_data_column)
        .rename(
            columns={
                "Amount (EUR)": "amount",
                "Date": "date",
                "Payee": "correspondent",
                "Payment reference": "description",
                "Account number": "iban",
            }
        )
        .dropna(subset=["date"])
        .pipe(to_lower)
        .pipe(__handle_transactions_between_n26_spaces)[transfer_columns]
    )
    return df
