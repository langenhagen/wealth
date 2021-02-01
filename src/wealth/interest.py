"""Functionality to calculate interest."""
import enum
import dataclasses
import functools
from typing import Any, List, Dict

import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.core.display import display
from IPython.display import Markdown

import wealth


class DepositTime(enum.Enum):
    """Specifies the the regular deposit time in a period."""

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
    values: Dict[Any, Any]


def calc_compound_interest(
    initial_amount: float,
    interest_rate: float,
    n_periods: int,
    n_interest_compounds_per_period: int = 1,
) -> float:
    """Calculate an amount with compoound interest given the input values."""
    final_amount = initial_amount * (
        1 + interest_rate / n_interest_compounds_per_period
    ) ** (n_periods * n_interest_compounds_per_period)
    return final_amount


def _build_account_history(
    start_amount: float,
    regular_deposit: float,
    deposit_freq: int,
    interest_rate: float,
    compound_freq: int,
    n_periods: int,
    regular_deposit_time: DepositTime,
    additional_events: List[Event],
) -> List[Event]:
    """Build a sorted history of events from which to derive compound interest.
    If events happen at the same time, additional prevents happen before
    compunds, compounds happen before deposits. The start amount comes as the
    first event."""

    # initial and client specified events
    events = [Event(0, EventType.DEPOSIT, {"amount": start_amount}), *additional_events]

    # regular deposits
    if regular_deposit_time == DepositTime.START:
        deposit_times = np.linspace(
            1 / deposit_freq, n_periods, n_periods * deposit_freq
        )
        for ts in deposit_times:
            events.append(
                Event(ts, EventType.REGULAR_DEPOSIT, {"amount": regular_deposit})
            )

    # interest compounds
    compound_times = np.linspace(
        1 / compound_freq, n_periods, n_periods * compound_freq
    )
    for ts in compound_times:
        events.append(
            Event(
                ts,
                EventType.INTEREST_PAYMENT,
                {"rate": interest_rate / compound_freq},
            )
        )

    # regular deposits
    if regular_deposit_time == DepositTime.END:
        deposit_times = np.linspace(
            1 / deposit_freq, n_periods, n_periods * deposit_freq
        )
        for ts in deposit_times:
            events.append(
                Event(ts, EventType.REGULAR_DEPOSIT, {"amount": regular_deposit})
            )

    events.sort(key=lambda event: event.timestamp)
    return events


def _calc_account_development(events: List[Event]) -> pd.DataFrame:
    """Calculate the account development given the list of times and events and
    return it as a Dataframe.
    If events happen at the same time, additional prevents happen before
    compounds, compounds happen before deposits. The start amount comes as the
    first event."""
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

    return pd.DataFrame(
        {"time": times, "type": types, "change": changes, "balance": balances}
    )


def _plot_account_development(df: pd.DataFrame):
    """Plot given dataframe to display its development both with its total
    balance and with only the self-deposited values without interest."""
    df_all = df[["time", "balance"]].groupby(["time"]).last()
    plt.step(df_all.index, df_all, where="post", label="Balance")
    mask = (df["type"] == "deposit") | (df["type"] == "regular deposit")
    df_deposits = df[mask][["time", "change"]].groupby(["time"]).sum().cumsum()
    plt.step(df_deposits.index, df_deposits, where="post", label="Own Deposits")


def _calc_interest_from_widgets(
    _,
    out_summary: widgets.Output,
    out_fig: widgets.Output,
    out_df: widgets.Output,
    fig: mpl.figure.Figure,
    txt_start_amount: widgets.FloatText,
    txt_regular_deposit: widgets.FloatText,
    txt_deposit_freq: widgets.IntText,
    txt_interest_rate: widgets.FloatText,
    txt_compound_freq: widgets.IntText,
    txt_periods: widgets.IntText,
    btn_deposit_time: widgets.ToggleButton,
    additional_events: List[Event],
):
    """Calculate the according account balances from the given widget's
    values and plot it."""
    events = _build_account_history(
        txt_start_amount.value,
        txt_regular_deposit.value,
        txt_deposit_freq.value,
        txt_interest_rate.value / 100,
        txt_compound_freq.value,
        txt_periods.value,
        btn_deposit_time.value,
        additional_events,
    )
    df = _calc_account_development(events)

    final_balance = df.iloc[-1]["balance"]
    increase_percent = round((final_balance / txt_start_amount.value - 1) * 100, 2)
    invested = df[(df["type"] == "deposit") | (df["type"] == "regular deposit")][
        "change"
    ].sum()
    interest_sum = df[df["type"] == "interest"]["change"].sum()
    out_summary.clear_output()
    with out_summary:
        display(
            Markdown(
                f"<br>The accumulated amount after {txt_periods.value} periods "
                f"is {wealth.Money(final_balance)}."
            )
        )
        display(Markdown(f"Money increased by {increase_percent}% from start."))
        display(Markdown(f"You invested {wealth.Money(invested)}."))
        display(Markdown(f"You received {wealth.Money(interest_sum)} interest."))
        display(
            Markdown(
                f"Interest-Investment ratio: {round(interest_sum/invested * 100, 2)}%."
            )
        )
    with out_fig:
        fig.clear()
        wealth.plot.setup_plot_and_axes(fig, "Account Development")
        _plot_account_development(df)
        plt.legend(loc="best", borderaxespad=0.1)
    out_df.clear_output()
    with out_df:
        wealth.plot.display_dataframe(df)


def interest(**kwargs):
    """Interactively estimate compound interest and plot an according graph.
    Also consider an optionally given list of Events into the calculation."""
    # import matplotlib.pyplot as plt
    plt.close("all")
    initial_amount = kwargs.get("initial_amount", 1000)
    regular_deposit = kwargs.get("regular_deposit", 100)
    interest_rate = kwargs.get("interest_rate", 4)
    periods = kwargs.get("periods", 10)
    deposits_per_period = kwargs.get("deposits_per_period", 12)
    compounds_per_period = kwargs.get("compounds_per_period", 12)
    deposit_at_period_start = kwargs.get("deposit_at_period_start", DepositTime.START)
    additional_events = kwargs.get("additional_events", [])
    show_transaction_table = kwargs.get("show_transaction_table", True)

    lbl_placeholder = widgets.Label("")
    lbl_start_amount = widgets.Label(value="Initial amount: ")
    txt_start_amount = widgets.BoundedFloatText(
        value=initial_amount, min=0.01, max=999999999, layout=wealth.plot.text_layout
    )
    lbl_regular_deposit = widgets.Label(value="Regular deposit: ")
    txt_regular_deposit = widgets.BoundedFloatText(
        value=regular_deposit, min=0, max=999999999, layout=wealth.plot.text_layout
    )
    lbl_regular_deposit_freq = widgets.Label(value="Deposits per period: ")
    txt_deposit_freq = widgets.BoundedIntText(
        value=deposits_per_period, min=1, max=999999999, layout=wealth.plot.text_layout
    )
    lbl_interest_rate = widgets.Label(value="Interest rate %: ")
    txt_interest_rate = widgets.BoundedFloatText(
        value=interest_rate, min=0, max=100, step=0.1, layout=wealth.plot.text_layout
    )
    lbl_compounds_freq = widgets.Label(value="Compounds per period: ")
    txt_compound_freq = widgets.BoundedIntText(
        value=compounds_per_period, min=1, max=999999999, layout=wealth.plot.text_layout
    )
    lbl_periods = widgets.Label(value="Periods: ")
    txt_periods = widgets.BoundedIntText(
        value=periods, min=0, layout=wealth.plot.text_layout
    )
    lbl_deposit_time = widgets.Label(value="Deposit at: ")
    btn_deposit_time = widgets.ToggleButtons(
        options={"Period Start": DepositTime.START, "Period End": DepositTime.END},
        value=deposit_at_period_start,
    )
    box = widgets.HBox(
        [
            widgets.VBox(
                [lbl_start_amount, lbl_regular_deposit, lbl_interest_rate, lbl_periods]
            ),
            widgets.VBox(
                [txt_start_amount, txt_regular_deposit, txt_interest_rate, txt_periods]
            ),
            widgets.VBox(
                [
                    lbl_placeholder,
                    lbl_regular_deposit_freq,
                    lbl_compounds_freq,
                    lbl_deposit_time,
                ]
            ),
            widgets.VBox(
                [
                    lbl_placeholder,
                    txt_deposit_freq,
                    txt_compound_freq,
                    btn_deposit_time,
                ]
            ),
        ]
    )
    out_summary = widgets.Output()
    out_fig = widgets.Output()

    with out_fig:
        fig = plt.figure(figsize=(10, 7), num="Account Development")

    out_df = widgets.Output()

    update_interest = functools.partial(
        _calc_interest_from_widgets,
        out_summary=out_summary,
        out_fig=out_fig,
        out_df=out_df,
        fig=fig,
        txt_start_amount=txt_start_amount,
        txt_regular_deposit=txt_regular_deposit,
        txt_deposit_freq=txt_deposit_freq,
        txt_interest_rate=txt_interest_rate,
        txt_compound_freq=txt_compound_freq,
        txt_periods=txt_periods,
        btn_deposit_time=btn_deposit_time,
        additional_events=additional_events,
    )
    txt_start_amount.observe(update_interest, "value")
    txt_regular_deposit.observe(update_interest, "value")
    txt_deposit_freq.observe(update_interest, "value")
    txt_interest_rate.observe(update_interest, "value")
    txt_compound_freq.observe(update_interest, "value")
    txt_periods.observe(update_interest, "value")
    btn_deposit_time.observe(update_interest, "value")

    display(Markdown("## Calculate Compound Interest"))
    display(box)
    display(Markdown("# Summary"))
    display(out_summary)
    display(Markdown("# Account Development"))
    display(out_fig)
    if show_transaction_table:
        display(Markdown("# Transaction Table"))
        display(out_df)
    update_interest(None)
