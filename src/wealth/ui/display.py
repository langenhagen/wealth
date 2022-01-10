"""Functions to display all kinds of Python objects in `Wealth`."""
from typing import Any, Iterable

import pandas as pd
from IPython.display import Markdown
from IPython.display import display as ipython_display
from IPython.display import display_html


def display(o: Any):
    """Display an object.
    Print strings as Markdown.
    Print dataframes and styles with `max_rows` set to None aka infinity,
    `max_colwitdth` set to inifinity and numeric precision set to 2."""
    options = {
        "display.max_rows": None,
        "display.max_colwidth": None,
        "display.precision": 2,
    }
    with pd.option_context(*[i for option in list(options.items()) for i in option]):
        if isinstance(o, pd.DataFrame):
            ipython_display(o.style)
        elif isinstance(o, str):
            ipython_display(Markdown(o))
        else:
            ipython_display(o)


# pylint:disable=protected-access
def display_side_by_side(dfs: Iterable[pd.DataFrame]):
    """Display the given dataframes/styles and the given titles side by side in
    an inline manner."""
    html_str = ""
    for df in dfs:
        style = df if isinstance(df, pd.io.formats.style.Styler) else df.style
        style.set_table_attributes("style='display: inline; padding: 10px;'")
        html_str += style._repr_html_()

    display_html(html_str, raw=True)
