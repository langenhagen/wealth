"""Retirement & pension related functionality."""
# import datetime as dt

import ipywidgets as widgets

import wealth


def _numeric_adjust_widgets(caption: str, min: float, max: float) -> widgets.HBox:
    """Return a HBox with a label, a text box and a linked slider."""
    label = widgets.Label(value=caption)
    text = widgets.BoundedFloatText(min=min, max=max, layout=wealth.plot.text_layout)
    slider = widgets.FloatSlider(readout=False, min=min, max=max)
    widgets.jslink((text, "value"), (slider, "value"))
    box = widgets.HBox([label, text, slider])
    return box


def pension_info():
    """Calculate and display interactive information about the pension."""
    # TODO

    # now = dt.datetime.now()
    # retirement_year = _numeric_adjust_widgets(
    #     "When do you retire?:", now.year, now.year + 100
    # )

    # when do you drop out of job life?
    #  take number from config but make it changeable

    # what's money worth then compared to now? ~60% ==> inflation
    #  take inflation rate from config

    # how many years do you plan to receive the pension money
    #  take number from config but make it changeable

    # how much do you spend atm ~ per day, per week, per month, per year?
    #  calc but adjustable

    # how much do you receive then from the govt then per month/year?
    #  from cfg user.government_pension but adjustable

    # how much did you already put aside extra?
    #  from cfg but adjustable

    # calculate how much you require per day/week/month/year: require = current_spend/inflation

    # calculate how much you need extra per day/week/month/year: require - receive

    # calculate how much you should put aside per day/week/month/year

    # addable options: interactively adjust how much you you should put aside - would receive - whats the difference from required would be
