"""
Google Document AI Integration for PocketPilot AI
Simple receipt parsing with safe fallbacks
"""

import os
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import re

from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions


# ------------------------------------------------------------------
# Main Document AI Client
# ------------------------------------------------------------------

class DocumentAIClient:
    """
    Minimal Document AI client for receipt processing
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        processor_id: Optional[str] = None,
        location: str = "us"
    ):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.processor_id = processor_id or os.getenv("DOCUMENT_AI_PROCESSOR_ID")
        self.location = location

        if not self.project_id or not self.processor_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT and DOCUMENT_AI_PROCESSOR_ID must be set")

        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)

        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )

    def process_receipt(self, file_bytes: bytes, mime_type: str) -> Dict:
        """
        Process receipt file and return extracted data
        """
        try:
            raw_document = documentai.RawDocument(
                content=file_bytes,
                mime_type=mime_type
            )

            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )

            result = self.client.process_document(request=request)
            document = result.document

            data = self._extract_basic_fields(document)

            return {
                "success": True,
                "data": data,
                "confidence": self._average_confidence(document)
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "data": None
            }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _extract_basic_fields(self, document: documentai.Document) -> Dict:
        """
        Extract only essential receipt fields
        """
        extracted = {
            "amount": None,
            "date": None,
            "merchant": None,
            "category": "General"
        }

        for entity in document.entities:
            if entity.confidence < 0.7:
                continue

            text = entity.mention_text

            if entity.type_ in ("total_amount", "amount"):
                extracted["amount"] = self._parse_amount(text)

            elif entity.type_ in ("receipt_date", "date"):
                extracted["date"] = self._parse_date(text)

            elif entity.type_ in ("supplier_name", "merchant_name"):
                extracted["merchant"] = text.strip()

        # Fallback to text scan if needed
        if not extracted["amount"] or not extracted["merchant"]:
            fallback = self._fallback_from_text(document.text)
            extracted.update({k: v for k, v in fallback.items() if v})

        extracted["category"] = self._auto_categorize(extracted["merchant"])
        return extracted

    def _fallback_from_text(self, text: str) -> Dict:
        """
        Very simple regex fallback
        """
        result = {}

        amt_match = re.search(r"(₹|Rs\.?)\s*(\d+(?:\.\d{2})?)", text)
        if amt_match:
            result["amount"] = float(amt_match.group(2))

        lines = text.splitlines()
        for line in lines[:5]:
            if len(line.strip()) > 3 and not any(char.isdigit() for char in line):
                result["merchant"] = line.strip()
                break

        return result

    def _parse_amount(self, value: str) -> Optional[float]:
        try:
            cleaned = re.sub(r"[₹Rs,\s]", "", value)
            return float(cleaned)
        except Exception:
            return None

    def _parse_date(self, value: str) -> datetime:
        try:
            return datetime.strptime(value.strip(), "%Y-%m-%d")
        except Exception:
            return datetime.now()

    def _auto_categorize(self, merchant: Optional[str]) -> str:
        if not merchant:
            return "General"

        m = merchant.lower()
        if any(k in m for k in ["food", "restaurant", "cafe", "zomato", "swiggy"]):
            return "Food"
        if any(k in m for k in ["uber", "ola", "taxi", "fuel"]):
            return "Transport"
        if any(k in m for k in ["mart", "store", "grocery", "dmart"]):
            return "Groceries"

        return "General"

    def _average_confidence(self, document: documentai.Document) -> float:
        if not document.entities:
            return 0.0
        return sum(e.confidence for e in document.entities) / len(document.entities)


# ------------------------------------------------------------------
# Mock Client (VERY IMPORTANT for demos & testing)
# ------------------------------------------------------------------

class MockDocumentAIClient:
    """
    Safe mock for demo mode
    """

    def process_receipt(self, file_bytes: bytes, mime_type: str) -> Dict:
        return {
            "success": True,
            "data": {
                "amount": 320.0,
                "date": datetime.now(),
                "merchant": "Demo Cafe",
                "category": "Food"
            },
            "confidence": 0.9
        }


# ------------------------------------------------------------------
# Simple helper
# ------------------------------------------------------------------

def get_document_client(use_mock: bool = False):
    if use_mock:
        return MockDocumentAIClient()
    return DocumentAIClient()
