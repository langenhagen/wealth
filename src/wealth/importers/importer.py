"""Provides utilities to import the account *.csv files in the folder `csv`.
The csv files have to match a certain naming pattern in order to map them to
different importers. See `__read_account_csvs()`."""
import re
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

import wealth.config
import wealth.importers.dkb_v23_giro
import wealth.importers.dkb_v23_visa
import wealth.importers.n26_mastercard
import wealth.importers.sparkasse_giro
from wealth.importers.common import transfer_columns
from wealth.util.transaction_type import TransactionType


def __create_transaction_type(row: pd.Series) -> TransactionType:
    """Create a TransactionType object from a dataframe row."""
    if isinstance(row["transaction_type"], TransactionType):
        return row["transaction_type"]

    accounts = wealth.config.get("accounts", {})
    ibans = [accounts[acc].get("iban", 0) for acc in accounts.keys()]
    if row["iban"] in ibans:
        return TransactionType.from_amount(row["amount"], is_internal=True)
    return TransactionType.from_amount(row["amount"], is_internal=False)


def __add_transaction_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Populate a column named transaction_type with values of type
    TransactionType to the given data frame and return the same DataFrame."""
    df["transaction_type"] = df.apply(__create_transaction_type, axis="columns")
    return df


def _append_all_data_column_with_transaction_type(
    df: pd.DataFrame, delimiter: str = "; "
) -> pd.DataFrame:
    """Append the transaction type value to the all_data."""
    df["all_data"] = (
        df["all_data"]
        + delimiter
        + " transaction_type: "
        + df["transaction_type"].astype(str)
    )
    return df


def __yield_files_with_suffix(
    directory: Path, suffix: str
) -> Iterable[Path]:
    """Yield all files with the given suffix in the given folder."""
    suffix_lower = suffix.lower()
    for file in directory.iterdir():
        if file.suffix.lower() == suffix_lower and file.is_file():
            yield file


def __create_offset_df(account_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Create a dataframe holding the account's configured initial offset."""
    accounts = wealth.config.get("accounts", {})
    return pd.DataFrame(
        {
            "account": account_name,
            "account_type": df["account_type"].iloc[0],
            "amount": accounts.get(account_name, {}).get("offset", 0),
            "date": df["date"].min(),
            "description": "<initial offset>",
        },
        index=[0],
    )


def __delay_incomes(df: pd.DataFrame) -> pd.DataFrame:
    """Guarantee that incomese virtually happen after all expenses at any given
    day."""
    df.loc[df["amount"] > 0, "date"] = df["date"] + pd.DateOffset(hours=1)
    return df


def __read_account_csvs() -> pd.DataFrame:
    """Import all account-related *.csv files in the folder `csv`. The files
    must match a naming pattern that the map `namepattern_2_importer`
    specifies."""
    namepattern_2_importer = {
        ".*dkb-v23-giro.*": wealth.importers.dkb_v23_giro.read_csv,
        ".*dkb-v23-visa.*": wealth.importers.dkb_v23_visa.read_csv,
        ".*n26-mastercard.*": wealth.importers.n26_mastercard.read_csv,
        ".*sparkasse-giro.*": wealth.importers.sparkasse_giro.read_csv,
    }
    dataframes = []
    processed_accounts = set()

    for file in __yield_files_with_suffix(Path.cwd() / "../csv", ".csv"):
        match = re.match(r"\d{4}-(.+)-.*", file.stem)
        if match is None:
            continue
        account_name = match.group(1)
        for regex, read_csv in namepattern_2_importer.items():
            if re.match(regex, file.stem):
                current_df = read_csv(str(file), account_name)
                if account_name in processed_accounts:
                    dataframes.append(current_df)
                else:
                    offset_df = __create_offset_df(account_name, current_df)
                    dataframes.extend([offset_df, current_df])
                    processed_accounts.add(account_name)
                break

    df = (
        pd.concat(dataframes)
        .reset_index()
        .pipe(__delay_incomes)
        .sort_values(by="date")
        .reset_index()[transfer_columns + ["transaction_type"]]
    )
    return df


def init() -> pd.DataFrame:
    """Read the file `accounts.yml` and import csv files from the folder `csv`
    as a DataFrame and add columns for to conveniently work working with the
    DataFrame. The resulting DataFrame contains the transaction information."""
    df = (
        __read_account_csvs()
        .pipe(__add_transaction_type_column)
        .pipe(_append_all_data_column_with_transaction_type)
        .replace(np.nan, "", regex=True)[
            [
                "date",
                "account",
                "amount",
                "description",
                "account_type",
                "correspondent",
                "iban",
                "transaction_type",
                "all_data",
            ]
        ]
    )
    return df
