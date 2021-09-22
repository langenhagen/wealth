"""Contains logic to import sparkasse giro csv files in the csv CAMT format."""
import datetime as dt

import pandas as pd

from wealth.importers.common import add_all_data_column, to_lower, transfer_columns


def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from Sparkasse giro accounts."""
    columns = {
        "Betrag": "amount",
        "Valutadatum": "date",
        "Beguenstigter/Zahlungspflichtiger": "correspondent",
        "Verwendungszweck": "description",
        "Kontonummer/IBAN": "iban",
    }

    df = (
        pd.read_csv(
            path,
            date_parser=lambda x: dt.datetime.strptime(x, "%d.%m.%y"),
            decimal=",",
            engine="python",
            parse_dates=["Valutadatum"],
            sep=";",
            thousands=None,
        )
        .assign(account=account_name, account_type="sparkasse", transaction_type=None)
        .pipe(add_all_data_column)
        .rename(columns=columns)
        .dropna(subset=["date"])
        .pipe(to_lower)[transfer_columns]
    )

    return df
