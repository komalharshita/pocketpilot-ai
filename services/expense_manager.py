import pandas as pd
import uuid
from datetime import datetime
from pathlib import Path

# ✅ Always resolve path relative to project root
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "expenses.csv"


def load_expenses():
    """
    Load expenses from CSV.
    Always returns a DataFrame with the correct columns.
    """
    if not DATA_PATH.exists():
        return pd.DataFrame(columns=[
            "id", "date", "type", "amount",
            "category", "merchant", "notes"
        ])

    df = pd.read_csv(DATA_PATH)

    # ✅ Ensure required columns exist (defensive coding)
    required_columns = [
        "id", "date", "type", "amount",
        "category", "merchant", "notes"
    ]

    for col in required_columns:
        if col not in df.columns:
            df[col] = ""

    return df[required_columns]


def add_expense(expense_type, amount, category, merchant, notes=""):
    """
    Add a new expense and persist it to CSV.
    """
    df = load_expenses()

    new_expense = {
        "id": str(uuid.uuid4()),
        "date": datetime.now().strftime("%Y-%m-%d"),
        "type": expense_type,
        "amount": float(amount),  # ✅ Ensure numeric
        "category": category,
        "merchant": merchant,
        "notes": notes
    }

    df = pd.concat(
        [df, pd.DataFrame([new_expense])],
        ignore_index=True
    )

    # ✅ Create file if missing, overwrite safely
    df.to_csv(DATA_PATH, index=False)

    return df
