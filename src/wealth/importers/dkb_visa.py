"""Contains logic to import DKB Visa csv files format."""
import pandas as pd

import wealth.importers.common as common


def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from Deutsche Kreditbank (DKB) visa accounts."""
    df = (
        pd.read_csv(
            path,
            date_parser=lambda x: pd.datetime.strptime(x, "%d%m%Y"),
            decimal=",",
            engine="python",
            parse_dates=["Belegdatum"],
            sep=";",
            skiprows=6,
            thousands=".",
        )
        .assign(account=account_name, account_type="dkb-visa")
        .pipe(common.add_all_data_column)
        .rename(
            columns={
                "Betrag (EUR)": "amount",
                "Belegdatum": "date",
                "Beschreibung": "description",
            }
        )
        .dropna(subset=["date"])
        .pipe(common.make_lowercase)[
            [*columns.values(), "account", "account_type", "all_data"]
        ]
    )
    return df
