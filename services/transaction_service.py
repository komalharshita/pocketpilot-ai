# services/transaction_service.py

from typing import List, Dict
from services.firebase_service import db
from services.transaction_model import validate_transaction

COLLECTION = "transactions"

def create_transaction(payload: Dict) -> str:
    """
    Validates and creates a transaction in Firestore.
    Returns the created document ID.
    """
    data = validate_transaction(payload)
    doc_ref = db.collection(COLLECTION).document()
    data["transaction_id"] = doc_ref.id
    doc_ref.set(data)
    return doc_ref.id

def get_user_transactions(user_id: str) -> List[Dict]:
    """
    Fetch all transactions for a user.
    """
    query = (
        db.collection(COLLECTION)
        .where("user_id", "==", user_id)
    )

    return [doc.to_dict() for doc in query.stream()]

def delete_transaction(user_id: str, transaction_id: str) -> None:
    """
    Delete a transaction if it belongs to the user.
    Firestore rules enforce ownership.
    """
    doc_ref = db.collection(COLLECTION).document(transaction_id)
    doc_ref.delete()
