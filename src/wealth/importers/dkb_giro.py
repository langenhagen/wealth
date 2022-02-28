"""Contains logic to import DKB giro csv files format."""
import pandas as pd

from wealth.importers.common import add_all_data_column, to_lower


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
        .rename(columns=columns)
        .pipe(add_all_data_column)
        .dropna(subset=["date"])
        .pipe(to_lower)[[*columns.values(), "account", "account_type", "all_data"]]
    )
    return df
