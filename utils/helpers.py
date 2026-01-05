"""
Utility functions for PocketPilot AI
Helper functions for formatting, validation, and common operations
"""

import os
from datetime import datetime
from typing import List, Dict, Tuple
import mimetypes

def validate_file(file_path: str) -> Tuple[bool, str]:
    """
    Validate uploaded file
    
    Args:
        file_path: Path to the uploaded file
    
    Returns:
        Tuple of (is_valid, message)
    """
    # Check if file exists
    if not os.path.exists(file_path):
        return False, "File not found"
    
    # Check file size (limit to 10MB)
    file_size = os.path.getsize(file_path)
    if file_size > 10 * 1024 * 1024:
        return False, "File size exceeds 10MB limit"
    
    # Check file type
    mime_type, _ = mimetypes.guess_type(file_path)
    allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'application/pdf']
    
    if mime_type not in allowed_types:
        return False, f"Unsupported file type: {mime_type}. Please upload JPEG, PNG, or PDF files."
    
    return True, "File is valid"

def get_mime_type(file_path: str) -> str:
    """
    Get MIME type of a file
    
    Args:
        file_path: Path to the file
    
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    
    # Default to application/pdf if unknown
    return mime_type or 'application/pdf'

def format_currency(amount: float, currency: str = 'USD') -> str:
    """
    Format currency amount
    
    Args:
        amount: Numeric amount
        currency: Currency code
    
    Returns:
        Formatted currency string
    """
    symbols = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥'
    }
    
    symbol = symbols.get(currency, '$')
    return f"{symbol}{amount:,.2f}"

def format_date(date_str: str) -> str:
    """
    Format date string for display
    
    Args:
        date_str: Date string in various formats
    
    Returns:
        Formatted date string
    """
    if date_str == 'Unknown':
        return date_str
    
    try:
        # Try common date formats
        for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%B %d, %Y')
            except ValueError:
                continue
        
        # If no format matches, return original
        return date_str
    
    except Exception:
        return date_str

def format_receipts_for_display(receipts: List[Dict]) -> List[List]:
    """
    Format receipt data for Gradio table display
    
    Args:
        receipts: List of receipt dictionaries
    
    Returns:
        List of lists for table display
    """
    if not receipts:
        return []
    
    formatted_rows = []
    
    for receipt in receipts:
        row = [
            format_date(receipt.get('transaction_date', 'Unknown')),
            receipt.get('merchant_name', 'Unknown'),
            format_currency(receipt.get('total_amount', 0), receipt.get('currency', 'USD')),
            receipt.get('category', 'Uncategorized'),
            receipt.get('id', '')
        ]
        formatted_rows.append(row)
    
    return formatted_rows

def calculate_spending_summary(receipts: List[Dict]) -> Dict:
    """
    Calculate spending summary from receipts
    
    Args:
        receipts: List of receipt dictionaries
    
    Returns:
        Dictionary with spending statistics
    """
    if not receipts:
        return {
            'total_spent': 0,
            'total_receipts': 0,
            'average_transaction': 0,
            'categories': {}
        }
    
    total_spent = sum(r.get('total_amount', 0) for r in receipts)
    categories = {}
    
    for receipt in receipts:
        category = receipt.get('category', 'Other')
        amount = receipt.get('total_amount', 0)
        categories[category] = categories.get(category, 0) + amount
    
    return {
        'total_spent': total_spent,
        'total_receipts': len(receipts),
        'average_transaction': total_spent / len(receipts) if receipts else 0,
        'categories': categories
    }

def create_success_message(message: str) -> str:
    """Create a success message with emoji"""
    return f"✅ {message}"

def create_error_message(message: str) -> str:
    """Create an error message with emoji"""
    return f"❌ {message}"

def create_info_message(message: str) -> str:
    """Create an info message with emoji"""
    return f"ℹ️ {message}"