# services/receipt_extractor.py

from datetime import datetime
from typing import Dict, Optional


# Common entity type mappings used by Invoice/Receipt parsers
AMOUNT_TYPES = {
    "total_amount",
    "invoice_total",
    "amount_due",
    "total",
}

DATE_TYPES = {
    "invoice_date",
    "purchase_date",
    "date",
}

MERCHANT_TYPES = {
    "supplier_name",
    "merchant_name",
    "vendor_name",
}


def _safe_float(value: str) -> Optional[float]:
    try:
        value = value.replace(",", "").replace("₹", "").strip()
        return float(value)
    except Exception:
        return None


def _safe_date(value: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(value, fmt)
        except Exception:
            continue
    return None


def extract_receipt_fields(document) -> Dict:
    """
    Extract normalized receipt fields from a Document AI document.
    """

    amount = None
    date = None
    merchant = None
    confidences = []

    for ent in document.entities:
        ent_type = ent.type_.lower()
        ent_value = ent.mention_text.strip()

        # Amount detection
        if ent_type in AMOUNT_TYPES and amount is None:
            parsed = _safe_float(ent_value)
            if parsed is not None:
                amount = parsed
                confidences.append(ent.confidence)

        # Date detection
        elif ent_type in DATE_TYPES and date is None:
            parsed = _safe_date(ent_value)
            if parsed:
                date = parsed
                confidences.append(ent.confidence)

        # Merchant detection
        elif ent_type in MERCHANT_TYPES and merchant is None:
            merchant = ent_value
            confidences.append(ent.confidence)

    avg_confidence = round(
        sum(confidences) / len(confidences), 2
    ) if confidences else 0.0

    return {
        "amount": amount,
        "date": date,
        "merchant": merchant,
        "confidence": avg_confidence,
    }
