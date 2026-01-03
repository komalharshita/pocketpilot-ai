# services/receipt_service.py

from datetime import datetime
from services.firebase_service import db
from services.transaction_service import create_transaction

RECEIPT_COLLECTION = "receipts"


def save_receipt_and_transaction(user_id: str, receipt_data: dict, category: str):
    """
    Saves receipt metadata and creates a linked expense transaction.
    """

    # 1. Create expense transaction
    transaction_payload = {
        "user_id": user_id,
        "type": "expense",
        "amount": receipt_data["amount"],
        "category": category,
        "date": receipt_data["date"] or datetime.utcnow(),
        "notes": f"Receipt: {receipt_data.get('merchant', '')}",
        "source": "receipt",
    }

    transaction_id = create_transaction(transaction_payload)

    # 2. Save receipt metadata
    receipt_ref = db.collection(RECEIPT_COLLECTION).document()
    receipt_ref.set({
        "receipt_id": receipt_ref.id,
        "user_id": user_id,
        "extracted_amount": receipt_data["amount"],
        "extracted_date": receipt_data["date"],
        "merchant_name": receipt_data.get("merchant"),
        "confidence": receipt_data.get("confidence", 0.0),
        "linked_transaction_id": transaction_id,
        "uploaded_at": datetime.utcnow(),
    })

    return transaction_id
