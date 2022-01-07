"""Holds the TransactionType class definition and related functioality."""
import enum


class TransactionType(enum.Enum):
    """Define transaction types that can happen in a savings account."""

    DEPOSIT = "deposit"
    INTEREST = "interest"
