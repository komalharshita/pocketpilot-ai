# services/analytics_data.py

import pandas as pd
from services.transaction_service import get_user_transactions

EXPECTED_COLUMNS = [
    "transaction_id",
    "type",
    "amount",
    "category",
    "date",
    "notes",
    "source",
]

def get_transactions_df(user_id: str) -> pd.DataFrame:
    """
    Fetch user transactions from Firestore
    and return a clean Pandas DataFrame.
    """
    transactions = get_user_transactions(user_id)

    if not transactions:
        return pd.DataFrame(columns=EXPECTED_COLUMNS)

    df = pd.DataFrame(transactions)

    # Ensure required columns exist
    for col in EXPECTED_COLUMNS:
        if col not in df.columns:
            df[col] = None

    # Normalize data types
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)
    df["category"] = df["category"].fillna("General")
    df["type"] = df["type"].str.lower()
    df["source"] = df["source"].str.lower()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.tz_localize(None)

    return df
