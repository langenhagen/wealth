"""Contains logic to import sparkasse giro csv files in the csv CAMT format."""

import pandas as pd

from wealth.importers.common import add_all_data_column, to_lower, transfer_columns


def __parse_sparkasse_dates(series: pd.Series) -> pd.Series:
    values = series.astype(str).str.strip()
    parsed = pd.to_datetime(values, format="%d.%m.%Y", errors="coerce")
    fallback = pd.to_datetime(values, format="%d.%m.%y", errors="coerce")
    return parsed.fillna(fallback)


def read_csv(path: str, account_name: str) -> pd.DataFrame:
    """Import csv data from Sparkasse giro accounts."""
    columns = {
        "Betrag": "amount",
        "Valutadatum": "date",
        "Beguenstigter/Zahlungspflichtiger": "correspondent",
        "Verwendungszweck": "description",
        "Kontonummer/IBAN": "iban",
    }

    min_reasonable_date = pd.Timestamp("1990-01-01")

    df = (
        pd.read_csv(
            path,
            decimal=",",
            engine="python",
            sep=";",
            thousands=None,
        )
        .assign(Valutadatum=lambda x: __parse_sparkasse_dates(x["Valutadatum"]))
        .assign(account=account_name, account_type="sparkasse")
        .rename(columns=columns)
        .pipe(add_all_data_column)
        .dropna(subset=["date"])
        .loc[lambda x: x["date"] >= min_reasonable_date]
        .pipe(to_lower)[transfer_columns]
    )

    return df
