"""
Firebase Manager
Handles Firestore operations
"""

import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from config.settings import Settings


class FirebaseManager:
    """Manages Firebase Firestore operations"""

    def __init__(self):
        try:
            if not firebase_admin._apps:
                cred = credentials.Certificate(
                    Settings.FIREBASE_SERVICE_ACCOUNT_PATH
                )
                firebase_admin.initialize_app(cred)

            self.db = firestore.client()
            print("✓ Firebase initialized successfully")

        except Exception as e:
            print(f"✗ Firebase initialization error: {e}")
            raise

    def save_receipt_data(self, receipt_data: Dict) -> str:
        """
        Save receipt data to Firestore
        """

        receipt_data["created_at"] = datetime.now()
        receipt_data["updated_at"] = datetime.now()

        doc_ref = self.db.collection("receipts").add(receipt_data)
        return doc_ref[1].id

    def get_all_receipts(self) -> List[Dict]:
        """
        Fetch all receipts
        """

        try:
            receipts = []
            docs = (
                self.db.collection("receipts")
                .order_by("created_at", direction=firestore.Query.DESCENDING)
                .stream()
            )

            for doc in docs:
                data = doc.to_dict()
                data["id"] = doc.id

                if "created_at" in data:
                    data["created_at"] = data["created_at"].strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                receipts.append(data)

            return receipts

        except Exception as e:
            print(f"✗ Firestore read error: {e}")
            return []

    def get_receipt_by_id(self, receipt_id: str) -> Optional[Dict]:
        """
        Get a receipt by document ID
        """

        try:
            doc = (
                self.db.collection("receipts")
                .document(receipt_id)
                .get()
            )

            if doc.exists:
                data = doc.to_dict()
                data["id"] = doc.id
                return data

            return None

        except Exception as e:
            print(f"✗ Firestore get error: {e}")
            return None

    def delete_receipt(self, receipt_id: str) -> bool:
        """
        Delete a receipt
        """

        try:
            self.db.collection("receipts").document(receipt_id).delete()
            return True
        except Exception as e:
            print(f"✗ Firestore delete error: {e}")
            return False
