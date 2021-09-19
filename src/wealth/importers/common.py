"""Contains common code for importing bank transaction csv files."""

# Columns that most transactions you import have.
transfer_columns = [
    "date",
    "account",
    "amount",
    "description",
    "account_type",
    "transaction_type",
    "all_data",
    "correspondent",
    "iban",
]
