"""Functionality to calculate interest."""
import dataclasses
import datetime as dt
import enum
import functools
from typing import Any, Dict, List

import dateutil.relativedelta
import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
from IPython.core.display import display
from IPython.display import Markdown

import wealth
import wealth.inflation
from wealth.plot import (
    create_inflation_widgets,
    display_df,
    setup_yearly_plot_and_axes,
    slim_text_layout,
    text_layout,
    wide_checkbox_layout,
)
from wealth.util.format import money_fmt

BoundedFloatText = widgets.BoundedFloatText
BoundedIntText = widgets.BoundedIntText
Checkbox = widgets.Checkbox
DatePicker = widgets.DatePicker
FloatText = widgets.FloatText
Label = widgets.Label
HBox = widgets.HBox
IntText = widgets.IntText
Output = widgets.Output
ToggleButtons = widgets.ToggleButtons
VBox = widgets.VBox


class DepositTime(enum.Enum):
    """Defines the the possible regular deposit times in a year."""

    START = enum.auto()
    END = enum.auto()


class EventType(enum.Enum):
    """Define event types that can happen in an account."""

    DEPOSIT = enum.auto()
    REGULAR_DEPOSIT = enum.auto()
    INTEREST_PAYMENT = enum.auto()


@dataclasses.dataclass
class Event:
    """Define events that can make an account history."""

    timestamp: float
    action: EventType
    values: Dict[str, Any]


def calc_compound_interest(P: float, r: float, t: int, n: int = 1) -> float:
    """Given the initial principal balance P, an interest rate r, the number of
    times interest applied per time period n and the number of time periods
    elapsed t, calculate and return the compound interest."""
    return P * (1 + r / n) ** (t * n)


def _build_account_history(
    start_amount: float,
    start_date: dt.date,
    regular_deposit: float,
    deposit_freq: int,
    interest_rate: float,
    compound_freq: int,
    n_years: int,
    regular_deposit_time: DepositTime,
    additional_events: List[Event],
) -> List[Event]:
    """Build a sorted history of events from which to derive compound interest.
    If events happen at the same time, additional prevents happen before
    compunds, compounds happen before deposits. The start amount comes as the
    first event."""

    # initial and client specified events
    events = [
        Event(start_date, EventType.DEPOSIT, {"amount": start_amount}),
        *additional_events,
    ]

    end_date = start_date + dateutil.relativedelta.relativedelta(years=n_years)
    one_year = start_date + dateutil.relativedelta.relativedelta(years=1)
    first_deposit_date = start_date + (one_year - start_date) / deposit_freq

    # regular deposits
    if regular_deposit_time == DepositTime.START:
        periods = n_years * deposit_freq
        for ts in pd.date_range(first_deposit_date, end_date, periods=periods):
            date = ts.to_pydatetime(warn=False).date()
            event = Event(date, EventType.REGULAR_DEPOSIT, {"amount": regular_deposit})
            events.append(event)

    # interest compounds
    first_compound_date = start_date + (one_year - start_date) / compound_freq
    periods = n_years * compound_freq
    for ts in pd.date_range(first_compound_date, end_date, periods=periods):
        date = ts.to_pydatetime(warn=False).date()
        event = Event(
            date, EventType.INTEREST_PAYMENT, {"rate": interest_rate / compound_freq}
        )
        events.append(event)

    # regular deposits
    if regular_deposit_time == DepositTime.END:
        periods = n_years * deposit_freq
        for ts in pd.date_range(first_deposit_date, end_date, periods=periods):
            date = ts.to_pydatetime(warn=False).date()
            event = Event(date, EventType.REGULAR_DEPOSIT, {"amount": regular_deposit})
            events.append(event)

    events.sort(key=lambda event: event.timestamp)
    return events


def _calc_account_development(
    events: List[Event], inflation_rate: float
) -> pd.DataFrame:
    """Calculate the account development given the list of times and events and
    return it as a Dataframe.
    If events happen at the same time, additional events happen before
    compounds, compounds happen before deposits. The start amount comes as the
    first event.
    Also add a column that contains values discounted by linear inflation."""
    events.sort(key=lambda event: event.timestamp)
    times = []
    types = []
    changes = []
    balances = []
    current_balance = 0
    for event in events:
        times.append(event.timestamp)
        if event.action == EventType.DEPOSIT:
            types.append("deposit")
            amount = event.values["amount"]
            changes.append(amount)
            current_balance += amount
        elif event.action == EventType.INTEREST_PAYMENT:
            types.append("interest")
            interest_amount = current_balance * event.values["rate"]
            changes.append(interest_amount)
            current_balance += interest_amount
        elif event.action == EventType.REGULAR_DEPOSIT:
            types.append("regular deposit")
            amount = event.values["amount"]
            changes.append(amount)
            current_balance += amount
        else:
            raise KeyError(f"Event with type: {event.action} not implemented")

        balances.append(current_balance)

    df = pd.DataFrame(
        {"time": times, "type": types, "change": changes, "balance": balances}
    )
    df["time"] = pd.to_datetime(df["time"])

    start_year = df["time"].dt.year.min()
    end_year = df["time"].dt.year.max()
    years_to_remaining_factors = wealth.inflation.years_to_remaining_factors(
        start_year, end_year, inflation_rate
    )
    df["discounted_balance"] = df["balance"] * df["time"].dt.year.map(
        years_to_remaining_factors
    )
    return df


def _plot_account_development(df: pd.DataFrame, inflation_rate: float):
    """Plot given dataframe to display its development both with its total
    balance and with only the self-deposited values without interest.
    Also plot inflation-discounted balances and deposits."""
    # balances
    df_all = df[["time", "balance"]].groupby(["time"]).last()
    plt.step(df_all.index, df_all, where="post", label="Balance")

    # own deposits
    mask = (df["type"] == "deposit") | (df["type"] == "regular deposit")
    df_deposits = df[mask][["time", "change"]].groupby(["time"]).sum().cumsum()
    plt.step(df_deposits.index, df_deposits, where="post", label="Own Deposits")

    # balances after inflation
    df_discounted = df[["time", "discounted_balance"]].groupby(["time"]).last()
    plt.step(
        df_discounted.index,
        df_discounted,
        where="post",
        label="Balance after Inflation",
    )

    # own deposits after inflation
    start_year = df_deposits.index.year.min()
    end_year = df_deposits.index.year.max()
    years_to_remaining_factors = wealth.inflation.years_to_remaining_factors(
        start_year, end_year, inflation_rate
    )
    df_deposits["discounted_deposits"] = df_deposits[
        "change"
    ] * df_deposits.index.year.map(years_to_remaining_factors)
    plt.step(
        df_deposits.index,
        df_deposits["discounted_deposits"],
        where="post",
        label="Own Deposits after Inflation",
    )


def _calc_interest_from_widgets(
    _,
    out_summary: Output,
    out_fig: Output,
    out_df: Output,
    fig: mpl.figure.Figure,
    txt_start_amount: FloatText,
    txt_start_date: DatePicker,
    txt_regular_deposit: FloatText,
    txt_deposit_freq: IntText,
    txt_interest_rate: FloatText,
    txt_compound_freq: IntText,
    txt_years: IntText,
    btn_deposit_time: ToggleButtons,
    txt_inflation: FloatText,
    additional_events: List[Event],
):
    """Calculate the according account balances from the given widget's
    values and plot it."""
    events = _build_account_history(
        txt_start_amount.value,
        txt_start_date.value,
        txt_regular_deposit.value,
        txt_deposit_freq.value,
        txt_interest_rate.value / 100,
        txt_compound_freq.value,
        txt_years.value,
        btn_deposit_time.value,
        additional_events,
    )
    df = _calc_account_development(events, txt_inflation.value)

    final_balance = df.iloc[-1]["balance"]
    increase_percent = (final_balance / txt_start_amount.value - 1) * 100
    invested = df[(df["type"] == "deposit") | (df["type"] == "regular deposit")][
        "change"
    ].sum()
    interest_sum = df[df["type"] == "interest"]["change"].sum()
    discounted_final_balance = df.iloc[-1]["discounted_balance"]

    summary_df = pd.DataFrame(
        index=[
            "accumulated value",
            "increase since start",
            "invested",
            "interest received",
            "interest-investment ratio",
        ],
        data={
            "value": [
                wealth.Money(final_balance),
                wealth.percent_fmt(increase_percent),
                wealth.Money(invested),
                wealth.Money(interest_sum),
                wealth.percent_fmt(interest_sum / invested * 100),
            ],
            "discounted value": [
                wealth.Money(discounted_final_balance),
                "",
                "",
                "",
                "",
            ],
        },
    )
    out_summary.clear_output()
    with out_summary:
        display(Markdown(f"After {txt_years.value} years:"))
        display(summary_df)
    with out_fig:
        fig.clear()
        setup_yearly_plot_and_axes(fig, "Account Development")
        _plot_account_development(df, txt_inflation.value)
        plt.legend(loc="best", borderaxespad=0.1)
    out_df.clear_output()
    df["change"] = df["change"].map(money_fmt())
    df["balance"] = df["balance"].map(money_fmt())
    df["discounted_balance"] = df["discounted_balance"].map(money_fmt())
    with out_df:
        display_df(df)


def _change_transaction_table_visibility(
    _,
    out_table: Output,
    out_df: Output,
    chk_show_transaction_table: Checkbox,
):
    """Display or hide the transaction table in the given output depending on
    the value of the given checkbox."""
    out_table.clear_output()
    if chk_show_transaction_table.value:
        with out_table:
            display(Markdown("# Transaction Table"))
            display(out_df)


# pylint:disable=too-many-statements
def interest(**kwargs):
    """Interactively estimate compound interest and plot an according graph.
    Also consider an optionally given list of Events into the calculation."""
    plt.close("all")
    initial_amount = kwargs.get("initial_amount", 1000)
    start_date = kwargs.get("start_date", dt.datetime.now().date())
    regular_deposit = kwargs.get("regular_deposit", 100)
    interest_rate = kwargs.get("interest_rate", 4)
    years = kwargs.get("years", 10)
    deposits_per_year = kwargs.get("deposits_per_year", 12)
    compounds_per_year = kwargs.get("compounds_per_year", 12)
    deposit_at_period_start = kwargs.get("deposit_at_period_start", DepositTime.START)
    additional_events = kwargs.get("additional_events", [])
    show_transaction_table = kwargs.get("show_transaction_table", True)
    default_inflation_rate = wealth.config["inflation_rate"]
    inflation_rate = kwargs.get("inflation_rate", default_inflation_rate)

    lbl_start_amount = Label(value="Initial amount: ")
    txt_start_amount = BoundedFloatText(
        value=initial_amount,
        min=0.01,
        max=999999999,
        layout=slim_text_layout,
    )
    lbl_start_date = Label(value="Start date: ")
    txt_start_date = DatePicker(value=start_date, layout=text_layout)
    lbl_regular_deposit = Label(value="Regular deposit: ")
    txt_regular_deposit = BoundedFloatText(
        value=regular_deposit, min=0, max=999999999, layout=slim_text_layout
    )
    lbl_regular_deposit_freq = Label(value="Deposits per year: ")
    txt_deposit_freq = BoundedIntText(
        value=deposits_per_year,
        min=1,
        max=999999999,
        layout=slim_text_layout,
    )
    lbl_interest_rate = Label(value="Interest rate %: ")
    txt_interest_rate = BoundedFloatText(
        value=interest_rate,
        min=0,
        max=1000,
        step=0.1,
        layout=slim_text_layout,
    )
    lbl_compounds_freq = Label(value="Compounds per year: ")
    txt_compound_freq = BoundedIntText(
        value=compounds_per_year,
        min=1,
        max=999999999,
        layout=slim_text_layout,
    )
    lbl_years = Label(value="Years: ")
    txt_years = BoundedIntText(value=years, min=0, layout=slim_text_layout)
    lbl_deposit_time = Label(value="Deposit at: ")
    btn_deposit_time = ToggleButtons(
        options={"Period Start": DepositTime.START, "Period End": DepositTime.END},
        value=deposit_at_period_start,
    )
    txt_inflation, hbox_inflation = create_inflation_widgets(inflation_rate)
    box = VBox(
        [
            HBox(
                [
                    VBox(
                        [
                            lbl_start_amount,
                            lbl_regular_deposit,
                            lbl_interest_rate,
                            lbl_years,
                        ]
                    ),
                    VBox(
                        [
                            txt_start_amount,
                            txt_regular_deposit,
                            txt_interest_rate,
                            txt_years,
                        ]
                    ),
                    VBox(
                        [
                            lbl_start_date,
                            lbl_regular_deposit_freq,
                            lbl_compounds_freq,
                            lbl_deposit_time,
                        ]
                    ),
                    VBox(
                        [
                            txt_start_date,
                            txt_deposit_freq,
                            txt_compound_freq,
                            btn_deposit_time,
                        ]
                    ),
                ]
            ),
            hbox_inflation,
        ]
    )
    out_fig = Output()
    with out_fig:
        fig = plt.figure(figsize=(10, 7), num="Account Development")

    out_summary = Output()
    out_df = Output()
    update_interest = functools.partial(
        _calc_interest_from_widgets,
        out_summary=out_summary,
        out_fig=out_fig,
        out_df=out_df,
        fig=fig,
        txt_start_amount=txt_start_amount,
        txt_start_date=txt_start_date,
        txt_regular_deposit=txt_regular_deposit,
        txt_deposit_freq=txt_deposit_freq,
        txt_interest_rate=txt_interest_rate,
        txt_compound_freq=txt_compound_freq,
        txt_years=txt_years,
        btn_deposit_time=btn_deposit_time,
        txt_inflation=txt_inflation,
        additional_events=additional_events,
    )
    txt_start_amount.observe(update_interest, "value")
    txt_start_date.observe(update_interest, "value")
    txt_regular_deposit.observe(update_interest, "value")
    txt_deposit_freq.observe(update_interest, "value")
    txt_interest_rate.observe(update_interest, "value")
    txt_compound_freq.observe(update_interest, "value")
    txt_years.observe(update_interest, "value")
    btn_deposit_time.observe(update_interest, "value")
    txt_inflation.observe(update_interest, "value")

    out_table = Output()
    chk_show_transaction_table = Checkbox(
        value=show_transaction_table,
        description="Show Transaction Table",
        indent=False,
        layout=wide_checkbox_layout,
    )
    change_transaction_table_visibility = functools.partial(
        _change_transaction_table_visibility,
        out_table=out_table,
        out_df=out_df,
        chk_show_transaction_table=chk_show_transaction_table,
    )
    chk_show_transaction_table.observe(change_transaction_table_visibility, "value")

    display(Markdown("## Calculate Compound Interest"))
    display(box)
    display(Markdown("# Summary"))
    display(out_summary)
    display(Markdown("# Account Development"))
    display(out_fig)
    display(chk_show_transaction_table)
    display(out_table)
    update_interest(None)
    change_transaction_table_visibility(None)
