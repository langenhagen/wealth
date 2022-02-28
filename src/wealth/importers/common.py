"""Contains common code for importing bank transaction csv files."""
import pandas as pd

# Columns that most transactions have.
transfer_columns = [
    "date",
    "account",
    "amount",
    "description",
    "account_type",
    "transaction_type",
    "all_data",
    "correspondent",
    "iban",
]


def add_all_data_column(df: pd.DataFrame, delimiter: str = "; ") -> pd.DataFrame:
    """Add a column named "all_data" to the given DataFrame with "all_data"
    being a concatenated string representation of all other columns, separated
    by the given delimiter.
    Return the same object that was passed in."""
    all_data = None
    for col in df:
        if all_data is None:
            all_data = col + ": " + df[col].astype(str)
        else:
            all_data += delimiter + col + ": " + df[col].astype(str)
    df["all_data"] = all_data
    return df


def to_lower(df: pd.DataFrame) -> pd.DataFrame:
    """Make all cells in a given DataFrame's columns of type "object" lowercase
    and return the DataFrame."""
    for col in df:
        if df[col].dtype.char == "O":
            df[col] = df[col].str.lower()
    return df
