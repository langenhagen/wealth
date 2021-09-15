"""Provides utilities to import all *.csv files in the folder csv.
The csv files have to match a certain naming pattern in order to map them to
different importers. See _read_all_csv_files()."""
import pathlib
import re
from typing import Iterable

import numpy as np
import pandas as pd

import wealth.config
import wealth.importers.common as import_common
import wealth.importers.dkb_giro
import wealth.importers.dkb_visa
import wealth.importers.n26_mastercard
import wealth.importers.sparkasse_giro
import wealth.util.transaction_type

TransactionType = wealth.util.transaction_type.TransactionType


def _create_transaction_type(row: pd.Series) -> TransactionType:
    """Create a TransactionType object from a dataframe row."""
    if row["transaction_type"]:
        return row["transaction_type"]

    accounts = wealth.config.get("accounts", {})
    ibans = [accounts[acc].get("iban", 0) for acc in accounts.keys()]
    if row["iban"] in ibans:
        return TransactionType.create_from_amount(row["amount"], is_internal=True)
    return TransactionType.create_from_amount(row["amount"], is_internal=False)


def _add_transaction_type_column(df: pd.DataFrame) -> pd.DataFrame:
    """Populate a column named transaction_type with values of type
    TransactionType to the given data frame and return the same DataFrame."""
    df["transaction_type"] = df.apply(_create_transaction_type, axis=1)
    return df


def _yield_files_with_suffix(
    directory: pathlib.Path, suffix: str
) -> Iterable[pathlib.Path]:
    """Yield all files with the given suffix in the given folder."""
    suffix_lower = suffix.lower()
    for file in directory.iterdir():
        if file.suffix.lower() == suffix_lower and file.is_file():
            yield file


def _create_offset_df(account_name: str, df: pd.DataFrame) -> pd.DataFrame:
    """Create a dataframe holding the account's configured initial offset."""
    accounts = wealth.config.get("accounts", {})
    account_type = df["account_type"].iloc[0]
    offset = accounts.get(account_name, {}).get("offset", 0)
    date = df["date"].min()
    return pd.DataFrame(
        {
            "account": account_name,
            "account_type": account_type,
            "amount": offset,
            "date": date,
            "description": "<initial offset>",
        },
        index=[0],
    )


def _delay_incomes(df: pd.DataFrame) -> pd.DataFrame:
    """Guarantee that cumsums of the amounts peak out towards negative amounts
    when sevaral transactions happen on the same day by delaying incomes
    so that they virtually happen after all expenses at any given day."""
    df.loc[df["amount"] > 0, "date"] = df["date"] + pd.DateOffset(hours=1)
    return df


def _strip_times(df: pd.DataFrame) -> pd.DataFrame:
    """Strip the times from the column `date`."""
    df["date"] = pd.to_datetime(df["date"].dt.date)
    return df


def _read_all_csv_files() -> pd.DataFrame:
    """Import all *.csv files in the folder "csv".
    The files must match a certain naming pattern that the map
    `namepattern_2_importer` specifies."""
    namepattern_2_importer = {
        ".*dkb-giro.*": wealth.importers.dkb_giro.read_csv,
        ".*dkb-visa.*": wealth.importers.dkb_visa.read_csv,
        ".*n26-mastercard.*": wealth.importers.n26_mastercard.read_csv,
        ".*sparkasse-giro.*": wealth.importers.sparkasse_giro.read_csv,
    }
    dataframes = []
    found_accounts = set()

    for file in _yield_files_with_suffix(pathlib.Path.cwd() / "../csv", ".csv"):
        if file.name == "track.csv":
            continue
        account_name = re.match(r"\d{4}-(.+)-.*", file.stem).group(1)
        for regex, read_csv in namepattern_2_importer.items():
            if re.match(regex, file.stem):
                current_df = read_csv(file, account_name)
                if account_name not in found_accounts:
                    offset_df = _create_offset_df(account_name, current_df)
                    found_accounts.add(account_name)
                    dataframes.extend([offset_df, current_df])
                else:
                    dataframes.append(current_df)
                break

    df = (
        pd.concat(dataframes)
        .reset_index()
        .pipe(_delay_incomes)
        .sort_values(by="date")
        .pipe(_strip_times)
        .set_index("date", drop=False)[import_common.transfer_columns]
    )
    return df


def _add_date_related_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add columns with year, month, weekday name and day of month from the
    given datetimeindex of the DataFrame and return the DataFrame."""
    return df.assign(
        year=df.index.year,
        month=df.index.month_name(),
        day_of_week=df.index.day_name(),
        day_of_month=df.index.day,
    )


def create_dataframe() -> pd.DataFrame:
    """Read the file accounts.yml and import csv files from the folder "csv"
    as a DataFrame and add columns for working working with `Wealth`.
    The resulting DataFrame is the main DataFrame that contains the
    transaction information."""
    df = (
        _read_all_csv_files()
        .pipe(_add_transaction_type_column)
        .pipe(_add_date_related_columns)
        .replace(np.nan, "", regex=True)[
            [
                "account",
                "amount",
                "description",
                "account_type",
                "correspondent",
                "iban",
                "transaction_type",
                "date",
                "year",
                "month",
                "day_of_week",
                "day_of_month",
                "all_data",
            ]
        ]
    )
    return df
