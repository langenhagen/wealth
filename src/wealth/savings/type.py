"""Holds the TransactionType class definition and related functioality."""
import enum


class TransactionType(enum.Enum):
    """Define transaction types that can happen in a savings account."""

    DEPOSIT = "deposit"
    INTEREST = "interest"

    def __str__(self) -> str:
        """Print the enum's value nicely."""
        return self.value
