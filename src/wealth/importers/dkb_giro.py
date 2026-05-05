"""Contains logic to import DKB CSV file format from last half of 2024 onwards."""

import pandas as pd

from wealth.importers.common import add_all_data_column, to_lower, transfer_columns


def __parse_dkb_dates(series: pd.Series) -> pd.Series:
    values = series.astype(str).str.strip()
    values = values.str.replace(r"^[^0-9]+", "", regex=True)
    parsed_short = pd.to_datetime(values, format="%d.%m.%y", errors="coerce")
    parsed_long = pd.to_datetime(values, format="%d.%m.%Y", errors="coerce")

    return parsed_short.fillna(parsed_long)


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
    min_reasonable_date = pd.Timestamp("1990-01-01")

    df = (
        pd.read_csv(
            path,
            decimal=",",
            dtype={"Buchungsdatum": "string"},
            engine="python",
            sep=",",
            skiprows=4,
            skip_blank_lines=True,
            thousands=".",
        )
        .assign(Buchungsdatum=lambda x: __parse_dkb_dates(x["Buchungsdatum"]))
        .assign(account=account_name, account_type="dkb-giro")
        .rename(columns=columns)
        .pipe(add_all_data_column)
        .dropna(subset=["date"])
        .loc[lambda x: x["date"] >= min_reasonable_date]
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
