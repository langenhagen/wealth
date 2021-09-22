"""Contains an enumeration to classify transactions as expenses, incomes or
internal transactions and according helper functions."""
import enum


class TransactionType(enum.Flag):
    """Describes whether a certain transaction describes an expense, an income
    and if that transaction is an internal transfer."""

    IN = enum.auto()
    OUT = enum.auto()
    INTERNAL_IN = enum.auto()
    INTERNAL_OUT = enum.auto()

    @staticmethod
    def create(is_expense: bool, is_internal: bool) -> "TransactionType":
        """Create a TransactionType object that fits the given traits."""
        if is_expense:
            return TransactionType.INTERNAL_OUT if is_internal else TransactionType.OUT
        return TransactionType.INTERNAL_IN if is_internal else TransactionType.IN

    @staticmethod
    def from_amount(amount: float, is_internal: bool = False) -> "TransactionType":
        """Create a TransactionType object given an amount."""
        return TransactionType.create(amount <= 0, is_internal)

    @staticmethod
    def from_row(row, is_internal: bool = False) -> "TransactionType":
        """Create a TransactionType object from a dataframe row."""
        return TransactionType.from_amount(row["amount"], False)

    def is_income(self) -> bool:
        """Determine if the given TransactionType is an income."""
        return self in (TransactionType.IN, TransactionType.INTERNAL_IN)

    def is_internal(self) -> bool:
        """Determine if the given TransactionType is an internal transaction."""
        return self in (TransactionType.INTERNAL_IN, TransactionType.INTERNAL_OUT)

    def __str__(self):
        """Print the transaction type nicely."""
        return str.lower(self.name)
