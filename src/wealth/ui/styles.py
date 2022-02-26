"""Common Dataframe styler definitions."""
from wealth.util.transaction_type import TransactionType

bar_color = "#d65fdf30"
shopping_color = "#ffff00dd"
wealth_color = "#e060e0dd"
green_color = "#00ff00aa"
red_color = "#ff0000aa"
yellow_color = "#ffff0044"

amount_border = {"border-left": "1.3px solid #cccccc"}
balance_border = {"border-left": "1.3px solid #ff0000"}
deposit_border = {"border-left": "1.3px solid #00aa00"}
interest_border = {"border-left": "1.3px solid #8888ff"}
ratio_border = {"border-left": "1.3px solid #aaaa00"}
soft_interest_border = {"border-left": "1.3px dotted #8888ff"}

monthly_border = {"border-left": "1px solid #e9435e"}
quarterly_border = {"border-left": "1px solid #d67d70"}
yearly_border = {"border-left": "1px solid #ecc371"}

shopping_border = {"border-left": f"1px solid {shopping_color}"}
wealth_border = {"border-left": f"1px solid {wealth_color}"}

green_fg = {"color": green_color}
red_fg = {"color": red_color}

shopping_bg = {"background": shopping_color, "color": "#000000ee"}
wealth_bg = {"background": wealth_color, "color": "#000000ee"}


def css_str(**kwargs):
    """Convert the given kwargs to a css style string."""
    s = ""
    for k, v in kwargs.items():
        s += f"{k}: {v};"
    return s


def conditional_negative_style(value) -> str:
    """Return a red font color if the given value is smaller than 0."""
    return f"color: {red_color};" if value < 0 else ""


def transaction_type_style(cols) -> list[str]:
    """Return a green back color if the given value is an income and return a
    yellow back color if the given value is an internal transactions."""
    type_ = cols["transaction_type"]
    if type_ == TransactionType.IN:
        color = f"background: {green_color}"
    elif type_ in [TransactionType.INTERNAL_IN, TransactionType.INTERNAL_OUT]:
        color = f"background: {yellow_color}"
    else:
        color = ""
    return [color] * len(cols)
