"""Contains logic to import DKB giro csv files format."""
import pandas as pd

import wealth.importers.common as common


def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from Deutsche Kreditbank (DKB) giro accounts."""
    columns = {
        "Betrag (EUR)": "amount",
        "Wertstellung": "date",
        "Auftraggeber / Beg�nstigter": "correspondent",
        "Verwendungszweck": "description",
        "Kontonummer": "iban",
    }
    df = (
        pd.read_csv(
            path,
            date_parser=lambda x: pd.datetime.strptime(x, "%d%m%Y"),
            decimal=",",
            engine="python",
            parse_dates=["Wertstellung"],
            sep=";",
            skiprows=5,
            thousands=".",
        )
        .assign(account=account_name, account_type="dkb-giro")
        .pipe(common.add_all_data_column)
        .rename(columns=columns)
        .dropna(subset=["date"])
        .pipe(common.make_lowercase)[
            [*columns.values(), "account", "account_type", "all_data"]
        ]
    )
    return df
