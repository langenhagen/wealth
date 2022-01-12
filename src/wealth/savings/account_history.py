"""Functionality to build an account history DataFrame including deposits from
CSV and interest from parameters."""
import pandas as pd

from wealth.inflation import years_to_remaining_factors

from .type import TransactionType


def build_account_history(
    imported: pd.DataFrame,
    interest_rate: float,
    tax_rate: float,
    inflation_rate: float,
) -> pd.DataFrame:
    """Given an account file, an annual interest rate, a tax rate and an annual
    inflation rate, create a DataFrame that contains an estimate of the account
    development."""
    imported["net amount"] = imported["amount"]

    start = imported["date"].min()
    end = imported["date"].max()
    # pylint: disable=no-member
    interests_data = {
        "date": pd.period_range(start, end, freq="M").end_time,
        "type": TransactionType.INTEREST,
        "note": None,
    }
    df = (
        pd.DataFrame(data=interests_data)
        .append(imported)
        .sort_values(by=["date"], kind="stable")
        .reset_index(drop=True)
    )

    interests = df["type"] == TransactionType.INTEREST
    interest_rate_part = interest_rate / 12
    for i, row in df[interests].iterrows():
        if row["type"] == TransactionType.INTEREST:
            df.loc[i, "amount"] = df.iloc[0:i]["amount"].sum() * interest_rate_part

    deposits = df["type"] == TransactionType.DEPOSIT
    after_tax = 1 - tax_rate
    df.loc[deposits, "net amount"] = df[deposits]["amount"]
    df.loc[interests, "net amount"] = df[interests]["amount"] * after_tax
    factors = years_to_remaining_factors(start.year, end.year, inflation_rate)
    inflation = df["date"].dt.year.map(factors)
    df["net amount after inflation"] = df["net amount"] * inflation
    df.loc[deposits, "deposit cumsum"] = df[deposits]["amount"].cumsum()
    df.loc[interests, "interest cumsum"] = df[interests]["amount"].cumsum()
    df.loc[interests, "net interest cumsum"] = (
        df[interests]["interest cumsum"] * after_tax
    )
    df["balance"] = df["amount"].cumsum()
    df["net balance"] = df["net amount"].cumsum()
    df["net balance after inflation"] = df["net balance"] * inflation

    return df


def summarize_history(df: pd.DataFrame) -> pd.DataFrame:
    """Build a summary dataframe from the given account history dataframe."""

    years = (df["date"].max() - df["date"].min()).days / 365
    balance = df["balance"].iat[-1]
    net_balance = df["net balance"].iat[-1]
    net_balance_after_inflation = df["net balance after inflation"].iat[-1]
    deposit = df["deposit cumsum"].iat[df["deposit cumsum"].last_valid_index()]
    last_interest_index = df["interest cumsum"].last_valid_index()
    interest = df["interest cumsum"].iat[last_interest_index]
    net_interest = df["net interest cumsum"].iat[last_interest_index]
    last_interest = df["amount"].iat[last_interest_index]
    last_net_interest = df["net amount"].iat[last_interest_index]
    last_net_interest_after_inflation = df["net amount after inflation"].iat[
        last_interest_index
    ]

    return pd.DataFrame.from_dict(
        {
            "years": years,
            "total accumulated amount": balance,
            "total net accumulated amount": net_balance,
            "total net accumulated amount after inflation": net_balance_after_inflation,
            "total invested amount": deposit,
            "total interest received": interest,
            "total net interest received": net_interest,
            "interest/deposit ratio": interest / deposit,
            "net interest/deposit ratio": net_interest / deposit,
            "last interest amount": last_interest,
            "last net interest amount": last_net_interest,
            "last net interest amount after inflation": last_net_interest_after_inflation,
        },
        orient="index",
        columns=["value"],
    )
