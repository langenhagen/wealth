"""Inflation related functionality."""
import datetime as dt
import functools

import ipywidgets as widgets
import matplotlib as mpl
import matplotlib.pyplot as plt
from IPython.core.display import display
from IPython.display import Markdown

import wealth
import wealth.config

BoundedFloatText = widgets.BoundedFloatText
FloatSlider = widgets.FloatSlider
FloatText = widgets.FloatText
HBox = widgets.HBox
Label = widgets.Label
IntText = widgets.IntText
Output = widgets.Output
VBox = widgets.VBox


def _calc_inflation_rate(
    start_cost: float, end_cost: float, start_year: int, end_year: int
) -> float:
    """Given the input values, return the according linear inflation rate."""
    return (end_cost / start_cost) ** (1 / (end_year - start_year)) - 1


def _get_birthday():
    """Return the user's birthday."""
    return wealth.config.config.get("retirement", {})["birthday"]


def _get_retirement_age():
    """Return the user's retirement age."""
    return wealth.config.config.get("retirement", {}).get("retirement_age", 67)


def _get_inflation_rate():
    """Get the user-configured intlation rate."""
    return wealth.config.config.get("inflation_rate", 2)


def _calc_inflation_rate_from_widgets(
    _,
    out: Output,
    txt_start_cost: FloatText,
    txt_start_year: IntText,
    txt_end_cost: FloatText,
    txt_end_year: IntText,
):
    """Calculate the according linear inflation rate from the given widgets'
    values."""
    if txt_start_cost.value == 0 or txt_end_year.value == txt_start_year.value:
        rate = "n/a"
    else:
        rate = _calc_inflation_rate(
            txt_start_cost.value,
            txt_end_cost.value,
            txt_start_year.value,
            txt_end_year.value,
        )
        rate = round(rate * 100, 2)

    out.clear_output()
    with out:
        display(Markdown(f"<br>The linear inflation rate is {rate}%"))


def inflation(
    start_cost: float = 100,
    start_year: int = dt.datetime.now().year,
    end_cost: float = 200,
    end_year: int = _get_birthday().year + _get_retirement_age(),
):
    """Interactively calculate inflation_rates."""
    lbl_start = Label(value="Start cost and year: ")
    txt_start_cost = FloatText(value=start_cost, layout=wealth.plot.text_layout)
    txt_start_year = IntText(value=start_year, layout=wealth.plot.text_layout)

    lbl_end = Label(value="End cost and year: ")
    txt_end_cost = FloatText(value=end_cost, layout=wealth.plot.text_layout)
    txt_end_year = IntText(value=end_year, layout=wealth.plot.text_layout)
    box = HBox(
        [
            VBox([lbl_start, lbl_end]),
            VBox([txt_start_cost, txt_end_cost]),
            VBox([txt_start_year, txt_end_year]),
        ]
    )
    out = Output()

    update_inflation_rate = functools.partial(
        _calc_inflation_rate_from_widgets,
        out=out,
        txt_start_cost=txt_start_cost,
        txt_start_year=txt_start_year,
        txt_end_cost=txt_end_cost,
        txt_end_year=txt_end_year,
    )
    txt_start_cost.observe(update_inflation_rate, "value")
    txt_start_year.observe(update_inflation_rate, "value")
    txt_end_cost.observe(update_inflation_rate, "value")
    txt_end_year.observe(update_inflation_rate, "value")

    display(Markdown("## Calculate Inflation Rates"))
    display(box)
    display(out)
    update_inflation_rate(None)


def _calc_inflated_value(
    start_cost: float, start_year: int, end_year: int, inflation_rate: float
) -> float:
    """Given the input values, return the according inflated cost."""
    return start_cost * (1 + inflation_rate / 100) ** (end_year - start_year)


def _plot_inflation_impact(
    start_cost: float, start_year: int, end_year: int, inflation_rate: float
):
    """Plot the impact of the inflation over time."""
    years = [dt.datetime(year, 1, 1) for year in range(start_year, end_year + 1)]
    values = []
    for year in range(start_year, end_year + 1):
        value = _calc_inflated_value(start_cost, start_year, year, inflation_rate)
        values.append(start_cost / value * 100)
    plt.plot(years, values)


def _calc_inflated_cost_from_widgets(
    _,
    out: Output,
    out_fig: Output,
    fig: mpl.figure.Figure,
    txt_start_cost: FloatText,
    txt_start_year: IntText,
    txt_end_year: IntText,
    txt_inflation: FloatText,
):
    """Calculate the according inflated cost from the given widgets' values and
    display it."""
    inflated_cost = _calc_inflated_value(
        txt_start_cost.value,
        txt_start_year.value,
        txt_end_year.value,
        txt_inflation.value,
    )
    inflated_cost = round(inflated_cost, 2)
    ratio = txt_start_cost.value / inflated_cost

    out.clear_output()
    with out:
        display(Markdown(f"<br>The inflated cost is {wealth.Money(inflated_cost)}"))
        display(
            Markdown(
                f"Money has {wealth.percent_fmt(ratio * 100)} of the value it had at start"
            )
        )
    with out_fig:
        fig.clear()
        wealth.plot.setup_yearly_plot_and_axes(
            fig, "Inflation Impact Over Time", xlabel="Year", ylabel="Value in %"
        )
        _plot_inflation_impact(
            txt_start_cost.value,
            txt_start_year.value,
            txt_end_year.value,
            txt_inflation.value,
        )


def future_worth(
    start_cost: float = 100,
    start_year: int = dt.datetime.now().year,
    end_year: int = _get_birthday().year + _get_retirement_age(),
    inflation_rate: float = _get_inflation_rate(),
):
    """Interactively estimate future costs subject to inflation."""
    lbl_start_cost = Label(value="Start cost: ")
    txt_start_cost = FloatText(value=start_cost, layout=wealth.plot.text_layout)
    lbl_start_year = Label(value="Start year: ")
    txt_start_year = IntText(value=start_year, layout=wealth.plot.text_layout)
    lbl_end_year = Label(value="End year: ")
    txt_end_year = IntText(value=end_year, layout=wealth.plot.text_layout)
    lbl_inflation = Label(value="Inflation rate %: ")
    txt_inflation = BoundedFloatText(
        min=0,
        max=100,
        step=0.01,
        value=inflation_rate,
        layout=wealth.plot.text_layout,
    )
    sld_inflation = FloatSlider(readout=False, min=0, max=100, step=0.01)
    widgets.jslink((txt_inflation, "value"), (sld_inflation, "value"))
    box = VBox(
        [
            HBox(
                [
                    lbl_start_cost,
                    txt_start_cost,
                    lbl_start_year,
                    txt_start_year,
                    lbl_end_year,
                    txt_end_year,
                ]
            ),
            HBox([lbl_inflation, txt_inflation, sld_inflation]),
        ]
    )
    out = Output()
    out_fig = Output()
    with out_fig:
        fig = plt.figure(figsize=(10, 7), num="Inflation Impact Over Time")

    update_inflated_cost = functools.partial(
        _calc_inflated_cost_from_widgets,
        out=out,
        out_fig=out_fig,
        fig=fig,
        txt_start_cost=txt_start_cost,
        txt_start_year=txt_start_year,
        txt_end_year=txt_end_year,
        txt_inflation=txt_inflation,
    )
    txt_start_cost.observe(update_inflated_cost, "value")
    txt_start_year.observe(update_inflated_cost, "value")
    txt_end_year.observe(update_inflated_cost, "value")
    txt_inflation.observe(update_inflated_cost, "value")

    display(Markdown("## Calculate Money's Future Worth"))
    display(box)
    display(out)
    display(out_fig)
    update_inflated_cost(None)
