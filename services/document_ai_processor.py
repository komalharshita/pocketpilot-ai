"""
DEMO Document AI Processor
--------------------------------
Google Document AI is NOT available in the free tier.

This file intentionally mocks receipt extraction
so the app remains functional and educational.
"""

from typing import Dict
import random


class DocumentAIProcessor:
    """Mock Document AI processor"""

    def __init__(self):
        print(
            "ℹ️ Document AI is running in DEMO mode "
            "(real API requires paid Google Cloud plan)"
        )

    def process_receipt(self, file_path: str, mime_type: str) -> Dict:
        """
        Simulate receipt extraction
        """

        merchants = [
            "Amazon",
            "Starbucks",
            "Walmart",
            "Zomato",
            "Uber Eats"
        ]

        categories = [
            "Shopping",
            "Dining",
            "Groceries",
            "Transportation"
        ]

        return {
            "merchant_name": random.choice(merchants),
            "transaction_date": "2025-01-05",
            "total_amount": round(random.uniform(10, 150), 2),
            "currency": "USD",
            "category": random.choice(categories),
            "raw_text": "Demo receipt text extracted by mock Document AI",
            "confidence": 0.90
        }
