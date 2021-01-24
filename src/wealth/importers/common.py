"""Contains common code for importing bank transaction csv files."""

# Columns that every transaction csv must have.
minimal_transfer_columns = [
    "date",
    "account",
    "amount",
    "description",
    "account_type",
    "transaction_type",
    "all_data",
]

# Columns that most transactions you import may have.
transfer_columns = minimal_transfer_columns + ["correspondent", "iban"]
