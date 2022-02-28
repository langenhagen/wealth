"""Contains logic to import DKB Visa csv files format."""
import pandas as pd

from wealth.importers.common import add_all_data_column, to_lower


def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from Deutsche Kreditbank (DKB) visa accounts."""
    columns = {
        "Betrag (EUR)": "amount",
        "Belegdatum": "date",
        "Beschreibung": "description",
    }
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
        .rename(columns=columns)
        .pipe(add_all_data_column)
        .dropna(subset=["date"])
        .pipe(to_lower)[[*columns.values(), "account", "account_type", "all_data"]]
    )
    return df
