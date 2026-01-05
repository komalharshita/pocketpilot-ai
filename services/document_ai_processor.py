# =========================
# File: services/document_ai_processor.py
# =========================
"""
MOCK / DEMO Document AI Processor
Document AI is NOT available in free tier.
"""

from typing import Dict
import random

class DocumentAIProcessor:
    """Demo processor that simulates Google Document AI output"""

    def __init__(self):
        print("ℹ️ Document AI running in DEMO mode (free-tier safe)")

    def process_receipt(self, file_path: str, mime_type: str) -> Dict:
        """
        Simulated receipt extraction
        """
        return {
            "merchant_name": random.choice(
                ["Amazon", "Starbucks", "Walmart", "Zomato"]
            ),
            "transaction_date": "2025-01-05",
            "total_amount": round(random.uniform(5, 120), 2),
            "currency": "USD",
            "category": "Demo Expense",
            "raw_text": "Demo receipt text",
            "confidence": 0.90,
        }
