"""
Utility helper functions for PocketPilot AI
Formatting, validation, and common helpers
"""

import os
import mimetypes
from datetime import datetime
from typing import List, Dict, Tuple


def validate_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate uploaded file

    - File must exist
    - Max size: 10MB
    - Supported: JPG, PNG, PDF
    """

    if not os.path.exists(file_path):
        return False, "File not found"

    # File size check (10MB)
    file_size = os.path.getsize(file_path)
    if file_size > 10 * 1024 * 1024:
        return False, "File size exceeds 10MB limit"

    mime_type, _ = mimetypes.guess_type(file_path)
    allowed_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "application/pdf"
    ]

    if mime_type not in allowed_types:
        return (
            False,
            f"Unsupported file type: {mime_type}. "
            "Upload JPG, PNG, or PDF."
        )

    return True, "File is valid"


def get_mime_type(file_path: str) -> str:
    """
    Return MIME type for file
    """

    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/pdf"


def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format numeric amount as currency string
    """

    symbols = {
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }

    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}"


def format_date(date_str: str) -> str:
    """
    Convert date string to readable format
    """

    if not date_str or date_str == "Unknown":
        return "Unknown"

    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(
                date_str, fmt
            ).strftime("%B %d, %Y")
        except ValueError:
            continue

    return date_str


def format_receipts_for_display(receipts: List[Dict]) -> List[List]:
    """
    Prepare receipt data for Gradio table
    """

    rows = []

    for receipt in receipts:
        rows.append([
            format_date(receipt.get("transaction_date")),
            receipt.get("merchant_name", "Unknown"),
            format_currency(
                receipt.get("total_amount", 0),
                receipt.get("currency", "USD")
            ),
            receipt.get("category", "Uncategorized"),
            receipt.get("id", "")
        ])

    return rows


def calculate_spending_summary(receipts: List[Dict]) -> Dict:
    """
    Calculate total, average, and category-wise spending
    """

    if not receipts:
        return {
            "total_spent": 0,
            "total_receipts": 0,
            "average_transaction": 0,
            "categories": {}
        }

    total_spent = sum(
        r.get("total_amount", 0) for r in receipts
    )

    categories = {}
    for receipt in receipts:
        category = receipt.get("category", "Other")
        amount = receipt.get("total_amount", 0)
        categories[category] = categories.get(category, 0) + amount

    return {
        "total_spent": total_spent,
        "total_receipts": len(receipts),
        "average_transaction": total_spent / len(receipts),
        "categories": categories
    }


def create_success_message(message: str) -> str:
    return f"✅ {message}"


def create_error_message(message: str) -> str:
    return f"❌ {message}"


def create_info_message(message: str) -> str:
    return f"ℹ️ {message}"
