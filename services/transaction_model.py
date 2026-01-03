# services/transaction_model.py

from datetime import datetime
from typing import Dict

ALLOWED_TYPES = {"expense", "income"}
ALLOWED_SOURCES = {"manual", "receipt"}

def validate_transaction(payload: Dict) -> Dict:
    """
    Validate and normalize a transaction payload.
    Raises ValueError on invalid input.
    Returns normalized payload.
    """
    required = ["user_id", "type", "amount", "category", "date", "source"]
    for field in required:
        if field not in payload:
            raise ValueError(f"Missing required field: {field}")

    if payload["type"] not in ALLOWED_TYPES:
        raise ValueError("Invalid transaction type")

    if payload["source"] not in ALLOWED_SOURCES:
        raise ValueError("Invalid transaction source")

    try:
        amount = float(payload["amount"])
        if amount <= 0:
            raise ValueError
    except Exception:
        raise ValueError("Amount must be a positive number")

    # Normalize fields
    payload["amount"] = amount
    payload["category"] = payload["category"].strip() or "General"
    payload["notes"] = payload.get("notes", "").strip()
    payload["created_at"] = datetime.utcnow()

    # Ensure date is datetime
    if payload["date"] is not None and not isinstance(payload["date"], datetime):
        raise ValueError("date must be a datetime object")

    return payload
