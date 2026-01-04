"""
Google Document AI Integration for PocketPilot AI
Handles receipt parsing and data extraction
"""

import os
from typing import Dict, Optional, Tuple, List
from datetime import datetime
import re
from google.cloud import documentai_v1 as documentai
from google.api_core.client_options import ClientOptions


class DocumentAIClient:
    """Client for processing receipts using Google Document AI"""
    
    def __init__(self, 
                 project_id: Optional[str] = None,
                 location: str = 'us',
                 processor_id: Optional[str] = None):
        """
        Initialize Document AI client
        
        Args:
            project_id: Google Cloud project ID
            location: Processor location (default: 'us')
            processor_id: Document AI processor ID
        """
        self.project_id = project_id or os.getenv('GOOGLE_CLOUD_PROJECT')
        self.location = location
        self.processor_id = processor_id or os.getenv('DOCUMENT_AI_PROCESSOR_ID')
        
        if not self.project_id or not self.processor_id:
            raise ValueError("Project ID and Processor ID must be provided or set in environment variables")
        
        # Initialize Document AI client
        opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
        self.client = documentai.DocumentProcessorServiceClient(client_options=opts)
        
        # Build processor name
        self.processor_name = self.client.processor_path(
            self.project_id, self.location, self.processor_id
        )
    
    def process_receipt(self, 
                       file_content: bytes, 
                       mime_type: str = 'image/jpeg') -> Dict:
        """
        Process a receipt and extract structured data
        
        Args:
            file_content: Raw file bytes
            mime_type: MIME type of the file (image/jpeg, image/png, application/pdf)
            
        Returns:
            Dictionary containing extracted fields
        """
        try:
            # Create the document
            raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)
            
            # Configure the process request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract and structure the data
            extracted_data = self._extract_fields(document)
            
            return {
                'success': True,
                'data': extracted_data,
                'raw_text': document.text,
                'confidence': self._calculate_confidence(document)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'data': None
            }
    
    def _extract_fields(self, document: documentai.Document) -> Dict:
        """
        Extract structured fields from Document AI response
        
        Args:
            document: Processed document object
            
        Returns:
            Dictionary with extracted fields
        """
        extracted = {
            'amount': None,
            'date': None,
            'merchant': None,
            'items': [],
            'category': 'General',
            'currency': 'INR'
        }
        
        # Extract entities
        for entity in document.entities:
            entity_type = entity.type_
            entity_value = entity.mention_text
            confidence = entity.confidence
            
            # Only use high-confidence extractions (>0.7)
            if confidence < 0.7:
                continue
            
            if entity_type == 'total_amount' or entity_type == 'amount':
                extracted['amount'] = self._parse_amount(entity_value)
            
            elif entity_type == 'receipt_date' or entity_type == 'date':
                extracted['date'] = self._parse_date(entity_value)
            
            elif entity_type == 'supplier_name' or entity_type == 'merchant_name':
                extracted['merchant'] = entity_value.strip()
            
            elif entity_type == 'line_item' or entity_type == 'item':
                extracted['items'].append({
                    'name': entity_value,
                    'confidence': confidence
                })
        
        # Fallback: Extract from raw text if entities not found
        if not extracted['amount'] or not extracted['date'] or not extracted['merchant']:
            fallback_data = self._extract_from_text(document.text)
            
            if not extracted['amount'] and fallback_data.get('amount'):
                extracted['amount'] = fallback_data['amount']
            
            if not extracted['date'] and fallback_data.get('date'):
                extracted['date'] = fallback_data['date']
            
            if not extracted['merchant'] and fallback_data.get('merchant'):
                extracted['merchant'] = fallback_data['merchant']
        
        # Auto-categorize based on merchant or items
        extracted['category'] = self._auto_categorize(extracted['merchant'], extracted['items'])
        
        return extracted
    
    def _extract_from_text(self, text: str) -> Dict:
        """
        Fallback method to extract data from raw text using regex
        
        Args:
            text: Raw OCR text
            
        Returns:
            Dictionary with extracted fields
        """
        extracted = {}
        
        # Extract amounts (₹ or Rs.)
        amount_patterns = [
            r'₹\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'Rs\.?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'Total:?\s*(\d+(?:,\d+)*(?:\.\d{2})?)',
            r'Amount:?\s*(\d+(?:,\d+)*(?:\.\d{2})?)'
        ]
        
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted['amount'] = self._parse_amount(match.group(1))
                break
        
        # Extract dates
        date_patterns = [
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{2,4})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted['date'] = self._parse_date(match.group(1))
                break
        
        # Extract merchant (usually in first few lines)
        lines = text.split('\n')
        for line in lines[:5]:
            line = line.strip()
            if len(line) > 3 and not any(char.isdigit() for char in line):
                extracted['merchant'] = line
                break
        
        return extracted
    
    def _parse_amount(self, amount_str: str) -> Optional[float]:
        """
        Parse amount string to float
        
        Args:
            amount_str: Amount as string
            
        Returns:
            Float value or None
        """
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[₹Rs.,\s]', '', amount_str)
            return float(cleaned)
        except (ValueError, AttributeError):
            return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Parse date string to datetime object
        
        Args:
            date_str: Date as string
            
        Returns:
            datetime object or None
        """
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d',
            '%d/%m/%y', '%d-%m-%y',
            '%d %b %Y', '%d %B %Y',
            '%b %d %Y', '%B %d %Y'
        ]
        
        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        # If no format matches, return current date
        return datetime.now()
    
    def _auto_categorize(self, merchant: Optional[str], items: List[Dict]) -> str:
        """
        Automatically categorize transaction based on merchant or items
        
        Args:
            merchant: Merchant name
            items: List of items purchased
            
        Returns:
            Category string
        """
        if not merchant:
            return 'General'
        
        merchant_lower = merchant.lower()
        
        # Define category keywords
        categories = {
            'Food': ['restaurant', 'cafe', 'food', 'pizza', 'burger', 'kitchen', 'dining', 'swiggy', 'zomato'],
            'Transport': ['uber', 'ola', 'taxi', 'metro', 'bus', 'transport', 'fuel', 'petrol'],
            'Groceries': ['supermarket', 'grocery', 'mart', 'store', 'reliance', 'dmart', 'bigbasket'],
            'Entertainment': ['cinema', 'movie', 'pvr', 'inox', 'game', 'entertainment'],
            'Shopping': ['shop', 'mall', 'amazon', 'flipkart', 'myntra', 'fashion'],
            'Health': ['pharmacy', 'medical', 'hospital', 'clinic', 'doctor', 'apollo'],
            'Education': ['book', 'stationery', 'college', 'university', 'course']
        }
        
        for category, keywords in categories.items():
            if any(keyword in merchant_lower for keyword in keywords):
                return category
        
        return 'General'
    
    def _calculate_confidence(self, document: documentai.Document) -> float:
        """
        Calculate overall confidence score for extraction
        
        Args:
            document: Processed document
            
        Returns:
            Confidence score (0-1)
        """
        if not document.entities:
            return 0.0
        
        confidences = [entity.confidence for entity in document.entities]
        return sum(confidences) / len(confidences) if confidences else 0.0
    
    def validate_extraction(self, extracted_data: Dict, min_confidence: float = 0.85) -> Tuple[bool, List[str]]:
        """
        Validate extracted data and return issues
        
        Args:
            extracted_data: Dictionary of extracted fields
            min_confidence: Minimum acceptable confidence score
            
        Returns:
            Tuple of (is_valid, list of issues)
        """
        issues = []
        
        if not extracted_data.get('amount'):
            issues.append("Amount not found or unclear")
        elif extracted_data['amount'] <= 0:
            issues.append("Invalid amount value")
        
        if not extracted_data.get('date'):
            issues.append("Date not found or unclear")
        
        if not extracted_data.get('merchant'):
            issues.append("Merchant name not found")
        
        is_valid = len(issues) == 0
        
        return is_valid, issues


class MockDocumentAIClient:
    """
    Mock client for testing without actual Document AI API
    Simulates receipt processing with predefined responses
    """
    
    def process_receipt(self, file_content: bytes, mime_type: str = 'image/jpeg') -> Dict:
        """
        Mock process receipt - returns sample data
        
        Args:
            file_content: File bytes (not used in mock)
            mime_type: MIME type (not used in mock)
            
        Returns:
            Mock extraction result
        """
        return {
            'success': True,
            'data': {
                'amount': 450.00,
                'date': datetime.now(),
                'merchant': 'Sample Restaurant',
                'items': [
                    {'name': 'Coffee', 'confidence': 0.95},
                    {'name': 'Sandwich', 'confidence': 0.92}
                ],
                'category': 'Food',
                'currency': 'INR'
            },
            'raw_text': 'SAMPLE RESTAURANT\nDate: 2024-01-15\nTotal: ₹450.00',
            'confidence': 0.90
        }
    
    def validate_extraction(self, extracted_data: Dict, min_confidence: float = 0.85) -> Tuple[bool, List[str]]:
        """Mock validation"""
        return True, []


# Helper functions

def process_receipt_file(file_path: str, 
                         project_id: Optional[str] = None,
                         processor_id: Optional[str] = None,
                         use_mock: bool = False) -> Dict:
    """
    Process a receipt file and return extracted data
    
    Args:
        file_path: Path to receipt image/PDF
        project_id: Google Cloud project ID
        processor_id: Document AI processor ID
        use_mock: Use mock client for testing
        
    Returns:
        Extraction result dictionary
    """
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # Determine MIME type
        if file_path.lower().endswith('.pdf'):
            mime_type = 'application/pdf'
        elif file_path.lower().endswith('.png'):
            mime_type = 'image/png'
        else:
            mime_type = 'image/jpeg'
        
        if use_mock:
            client = MockDocumentAIClient()
        else:
            client = DocumentAIClient(project_id, processor_id=processor_id)
        
        return client.process_receipt(file_content, mime_type)
    
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'data': None
        }


# Example usage
if __name__ == "__main__":
    # Test with mock client
    print("Testing with Mock Document AI Client...")
    mock_client = MockDocumentAIClient()
    result = mock_client.process_receipt(b"dummy content")
    
    print("\nExtraction Result:")
    print(f"Success: {result['success']}")
    print(f"Amount: ₹{result['data']['amount']}")
    print(f"Merchant: {result['data']['merchant']}")
    print(f"Category: {result['data']['category']}")
    print(f"Confidence: {result['confidence']:.2%}")
    
    # Validation
    is_valid, issues = mock_client.validate_extraction(result['data'])
    print(f"\nValidation: {'✓ Passed' if is_valid else '✗ Failed'}")
    if issues:
        print("Issues:", ", ".join(issues))