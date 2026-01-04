"""
Document AI Service - Extract data from receipt images/PDFs
Uses Google Document AI for intelligent data extraction
"""

import streamlit as st
from typing import Dict, Optional
from datetime import datetime
import re

try:
    from google.cloud import documentai_v1 as documentai
    from google.api_core.client_options import ClientOptions
    DOCUMENT_AI_AVAILABLE = True
except ImportError:
    DOCUMENT_AI_AVAILABLE = False


class DocumentAIService:
    """
    Service for processing receipts with Google Document AI
    Extracts merchant, amount, date, and line items
    """
    
    def __init__(self):
        """Initialize Document AI client"""
        if not DOCUMENT_AI_AVAILABLE:
            raise ImportError("google-cloud-documentai not installed")
        
        # Get configuration from Streamlit secrets
        try:
            doc_ai_config = st.secrets.get("document_ai", {})
            
            self.project_id = doc_ai_config.get("project_id", "")
            self.location = doc_ai_config.get("location", "us")
            self.processor_id = doc_ai_config.get("processor_id", "")
            
            if not self.project_id or not self.processor_id:
                raise ValueError("Document AI configuration missing")
            
            # Initialize client
            opts = ClientOptions(
                api_endpoint=f"{self.location}-documentai.googleapis.com"
            )
            self.client = documentai.DocumentProcessorServiceClient(
                client_options=opts
            )
            
            # Build processor name
            self.processor_name = self.client.processor_path(
                self.project_id,
                self.location,
                self.processor_id
            )
            
        except Exception as e:
            raise ValueError(f"Failed to initialize Document AI: {str(e)}")
    
    def extract_receipt_data(
        self, 
        file_bytes: bytes, 
        mime_type: str
    ) -> Dict:
        """
        Extract structured data from receipt using Document AI
        
        Args:
            file_bytes: Receipt file content
            mime_type: MIME type of file
            
        Returns:
            Dictionary with extracted data and success status
        """
        try:
            # Create raw document
            raw_document = documentai.RawDocument(
                content=file_bytes,
                mime_type=mime_type
            )
            
            # Create process request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            # Process document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract fields
            extracted_data = self._extract_fields(document)
            
            return {
                'success': True,
                'data': extracted_data,
                'confidence': self._calculate_confidence(document)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': {}
            }
    
    def _extract_fields(self, document: documentai.Document) -> Dict:
        """
        Extract specific fields from processed document
        
        Args:
            document: Processed document from Document AI
            
        Returns:
            Dictionary with extracted fields
        """
        extracted = {
            'merchant': None,
            'amount': None,
            'date': None,
            'items': []
        }
        
        # Extract from entities
        for entity in document.entities:
            entity_type = entity.type_
            text = entity.mention_text.strip()
            confidence = entity.confidence
            
            # Only use high confidence extractions
            if confidence < 0.6:
                continue
            
            # Merchant/Supplier
            if entity_type in ['supplier_name', 'merchant_name', 'supplier']:
                extracted['merchant'] = text
            
            # Total amount
            elif entity_type in ['total_amount', 'amount', 'total']:
                extracted['amount'] = self._parse_amount(text)
            
            # Date
            elif entity_type in ['receipt_date', 'date', 'transaction_date']:
                extracted['date'] = self._parse_date(text)
            
            # Line items
            elif entity_type in ['line_item', 'item']:
                if text and len(text) > 2:
                    extracted['items'].append(text)
        
        # Fallback: extract from text if fields are missing
        if not extracted['merchant'] or not extracted['amount']:
            fallback = self._fallback_extraction(document.text)
            
            if not extracted['merchant']:
                extracted['merchant'] = fallback.get('merchant')
            if not extracted['amount']:
                extracted['amount'] = fallback.get('amount')
            if not extracted['date']:
                extracted['date'] = fallback.get('date')
        
        # Set defaults
        if not extracted['merchant']:
            extracted['merchant'] = 'Unknown Merchant'
        if not extracted['amount']:
            extracted['amount'] = 0.0
        if not extracted['date']:
            extracted['date'] = str(datetime.now().date())
        
        return extracted
    
    def _fallback_extraction(self, text: str) -> Dict:
        """
        Simple regex-based fallback extraction
        
        Args:
            text: Raw text from document
            
        Returns:
            Dictionary with extracted fields
        """
        result = {}
        
        # Extract amount (look for ₹ or Rs. followed by numbers)
        amount_patterns = [
            r'(?:₹|Rs\.?|INR)\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'(?:Total|TOTAL|Grand\s+Total).*?(\d+(?:,\d+)*(?:\.\d{2})?)',
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                amount_str = match.group(1).replace(',', '')
                try:
                    result['amount'] = float(amount_str)
                    break
                except:
                    pass
        
        # Extract merchant (usually in first few lines)
        lines = text.strip().split('\n')
        for line in lines[:5]:
            line = line.strip()
            # Look for lines without numbers that are reasonable length
            if line and 3 < len(line) < 50 and not any(c.isdigit() for c in line):
                result['merchant'] = line
                break
        
        # Extract date (look for common date patterns)
        date_patterns = [
            r'(\d{2}[/-]\d{2}[/-]\d{4})',
            r'(\d{4}[/-]\d{2}[/-]\d{2})',
            r'(\d{2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result['date'] = match.group(1)
                break
        
        return result
    
    def _parse_amount(self, text: str) -> float:
        """
        Parse amount from text string
        
        Args:
            text: Amount string
            
        Returns:
            Float amount
        """
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[₹Rs,\s]', '', text)
            return float(cleaned)
        except:
            return 0.0
    
    def _parse_date(self, text: str) -> str:
        """
        Parse and normalize date
        
        Args:
            text: Date string
            
        Returns:
            Normalized date string (YYYY-MM-DD)
        """
        try:
            # Try multiple date formats
            formats = [
                '%Y-%m-%d',
                '%d-%m-%Y',
                '%d/%m/%Y',
                '%Y/%m/%d',
                '%d %b %Y',
                '%d %B %Y',
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(text.strip(), fmt)
                    return dt.strftime('%Y-%m-%d')
                except:
                    continue
            
            # If nothing works, return today's date
            return str(datetime.now().date())
            
        except:
            return str(datetime.now().date())
    
    def _calculate_confidence(self, document: documentai.Document) -> float:
        """
        Calculate average confidence score
        
        Args:
            document: Processed document
            
        Returns:
            Average confidence (0-1)
        """
        if not document.entities:
            return 0.0
        
        total = sum(entity.confidence for entity in document.entities)
        return round(total / len(document.entities), 2)
