"""Common Dataframe styler definitions."""
from wealth.util.transaction_type import TransactionType


def red_fg(value) -> str:
    """Return a red font color if the given value is smaller than 0."""
    return "color: #ff0000aa;" if value < 0 else None


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