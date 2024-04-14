"""Contains logic to import DKB CSV file format from 2024 on."""

import datetime as dt

import pandas as pd

from wealth.importers.common import add_all_data_column, to_lower, transfer_columns


def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from Deutsche Kreditbank (DKB) giro accounts."""
    columns = {
        "Betrag (€)": "amount",
        "Buchungsdatum": "date",
        "Zahlungsempfänger*in": "correspondent",
        "Zahlungspflichtige*r": "incoming_correspondent",
        "Verwendungszweck": "description",
        "IBAN": "iban",
    }
    df = (
        pd.read_csv(
            path,
            date_parser=lambda x: dt.datetime.strptime(x, "%d.%m.%y"),
            decimal=",",
            engine="python",
            parse_dates=["Buchungsdatum"],
            sep=";",
            skiprows=4,
            thousands=".",
        )
        .assign(account=account_name, account_type="dkb-giro")
        .rename(columns=columns)
        .pipe(add_all_data_column)
        .dropna(subset=["date"])
        .pipe(to_lower)
    )

    df["correspondent"] = df.apply(
        lambda row: (
            row["incoming_correspondent"] if row["amount"] > 0 else row["correspondent"]
        ),
        axis=1,
    )
    df = df[transfer_columns]

    return df
