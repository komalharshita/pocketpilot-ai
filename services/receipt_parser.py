import re
from datetime import datetime


def extract_amount(text):
    """
    Extracts total amount from receipt text.
    """
    patterns = [
        r"total[:\s]*₹?\s?(\d+(\.\d{1,2})?)",
        r"amount[:\s]*₹?\s?(\d+(\.\d{1,2})?)"
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None

def extract_date(text):
    """
    Extracts date from receipt text.
    """
    date_patterns = [
        r"(\d{2}/\d{2}/\d{4})",
        r"(\d{4}-\d{2}-\d{2})"
    ]

    for pattern in date_patterns:
        match = re.search(pattern, text)
        if match:
            try:
                date = datetime.strptime(match.group(1), "%d/%m/%Y")
                return date.strftime("%Y-%m-%d")
            except ValueError:
                pass

    return datetime.now().strftime("%Y-%m-%d")

def extract_merchant(text):
    """
    Uses first non-empty line as merchant name.
    """
    lines = text.strip().splitlines()

    for line in lines:
        line = line.strip()
        if len(line) > 3:
            return line

    return "Unknown Merchant"

def parse_receipt_text(text):
    """
    Converts OCR text into structured expense data.
    """
    return {
        "merchant": extract_merchant(text),
        "date": extract_date(text),
        "amount": extract_amount(text),
        "category": "Uncategorized"
    }
