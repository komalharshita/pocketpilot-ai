"""
Utility functions for PocketPilot AI
Helper functions for formatting, validation, and common operations
"""

import os
from datetime import datetime
from typing import List, Dict, Tuple
import mimetypes

def validate_file(file_path: str) -> Tuple[bool, str]:
    """Validate uploaded file"""
    if not os.path.exists(file_path):
        return False, "File not found"
    
    file_size = os.path.getsize(file_path)
    if file_size > 10 * 1024 * 1024:
        return False, "File size exceeds 10MB limit"
    
    mime_type, _ = mimetypes.guess_type(file_path)
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
    
    if mime_type not in allowed_types:
        return False, f"Unsupported file type. Please upload JPEG, PNG, or PDF files."
    
    return True, "File is valid"

def get_mime_type(file_path: str) -> str:
    """Get MIME type of a file"""
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/pdf'

def format_currency(amount: float, currency: str = 'INR') -> str:
    """Format currency amount in Indian Rupees"""
    return f"₹{amount:,.2f}"

def format_date(date_str: str) -> str:
    """Format date string for display"""
    if date_str == 'Unknown':
        return date_str
    
    try:
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str

def format_receipts_for_display(receipts: List[Dict]) -> List[List]:
    """
    Format receipt data for Gradio table display
    Assumes dashboard already normalized the schema.
    """
    rows = []

    for r in receipts:
        rows.append([
            r["date"],
            r["merchant"],
            format_currency(r["amount"]),
            r["category"],
            r["id"]
        ])

    return rows


def calculate_spending_summary(receipts: List[Dict]) -> Dict:
    """Calculate spending summary from receipts"""
    if not receipts:
        return {
            'total_spent': 0,
            'total_receipts': 0,
            'average_transaction': 0,
            'categories': {}
        }
    
    total_spent = sum(r.get('amount', 0) for r in receipts)
    categories = {}
    
    for receipt in receipts:
        category = receipt.get('category', 'Other')
        amount = receipt.get('amount', 0)
        categories[category] = categories.get(category, 0) + amount
    
    return {
        'total_spent': total_spent,
        'total_receipts': len(receipts),
        'average_transaction': total_spent / len(receipts) if receipts else 0,
        'categories': categories
    }

def create_success_message(message: str) -> str:
    """Create a success message"""
    return f"✅ {message}"

def create_error_message(message: str) -> str:
    """Create an error message"""
    return f"❌ {message}"

def generate_short_id(full_id: str) -> str:
    """Generate short readable ID from UUID"""
    import hashlib
    hash_obj = hashlib.md5(full_id.encode())
    hex_dig = hash_obj.hexdigest()[:7].upper()
    return hex_dig