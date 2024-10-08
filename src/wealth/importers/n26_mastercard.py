"""Contains logic to import N26 giro csv files."""
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

    """Filter all rows that depict transactions between account-internal N26 spaces."""

    internal_account_names = df["Account Name"].dropna().unique()

    mask = df["Account Name"].isin(internal_account_names) & df["correspondent"].isin(
        internal_account_names
    )

    internal = df[mask].copy()
    df = df[~mask]

    internal["transaction_type"] = internal.apply(
        __create_internal_transaction_type, axis="columns"
    )

    internal.loc[internal["correspondent"] != "main account", "correspondent"] = (
        internal["account"] + " " + internal["correspondent"]
    )
    internal.loc[internal["correspondent"] == "main account", "correspondent"] = (
        internal["account"]
    )
    internal.loc[internal["Account Name"] != "main account", "account"] = (
        internal["account"] + " " + internal["Account Name"]
    )

    # Combine the internal transactions back with the main dataframe
    df = pd.concat([df, internal])

    return df

def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from N26 giro/mastercard accounts and consider n26's
    sub-accounts."""
    columns = {
        "Booking Date": "date",
        "Partner Name": "correspondent",
        "Payment Reference": "description",
        "Partner Iban": "iban",
        "Amount (EUR)": "amount",
    }
    df = (
        pd.read_csv(
            path,
            date_parser=lambda x: dt.datetime.strptime(x, "%Y-%m-%d"),
            decimal=".",
            engine="python",
            parse_dates=["Booking Date"],
            sep=",",
            thousands=None,
        )
        .assign(account=account_name, account_type="n26")
        .rename(columns=columns)
        .pipe(add_all_data_column)
        .dropna(subset=["date"])
        .pipe(to_lower)
        .pipe(__handle_transactions_between_n26_spaces)[
            transfer_columns + ["transaction_type"]
        ]
    )
    return df
