"""Common Dataframe styler definitions."""
from wealth.util.transaction_type import TransactionType


def red_fg(value) -> str:
    """Return a red font color if the given value is smaller than 0."""
    return "color: #ff0000aa;" if value < 0 else ""


def red_green_fg(value) -> str:
    """Return a green font color if the given value is greater or equal than 0,
    else return a red font."""
    return "color: #ff0000aa;" if value < 0 else "color: #00ff00aa;"


def green_yellow_bg(cols) -> list[str]:
    """Return a green back color if the given value is an income and return a
    yellow back color if the given value is an internal transactions."""
    type_ = cols["transaction_type"]
    if type_ == TransactionType.IN:
        color = "background: #00ff0044"
    elif type_ in [TransactionType.INTERNAL_IN, TransactionType.INTERNAL_OUT]:
        color = "background: #ffff0044"
    else:
        color = ""
    return [color] * len(cols)


amount_border = {"border-left": "1.3px solid #cccccc"}
balance_border = {"border-left": "1.3px solid #ff0000"}
deposit_border = {"border-left": "1.3px solid #00aa00"}
interest_border = {"border-left": "1.3px solid #8888ff"}
ratio_border = {"border-left": "1.3px solid #aaaa00"}
soft_interest_border = {"border-left": "1.3px dotted #8888ff"}

monthly_border = {"border-left": "1px solid #e9435e"}
quarterly_border = {"border-left": "1px solid #d67d70"}
yearly_border = {"border-left": "1px solid #ecc371"}

bar_color = "#d65fdf30"
