"""
Google Document AI Processor for receipt parsing
Extracts structured data from receipt images and PDFs
"""

from google.cloud import documentai_v1 as documentai
from typing import Dict, Optional
from config.settings import Settings

class DocumentAIProcessor:
    """Processes receipts using Google Document AI"""
    
    def __init__(self):
        """Initialize Document AI client"""
        try:
            self.client = documentai.DocumentProcessorServiceClient()
            
            # Build the processor name
            self.processor_name = self.client.processor_path(
                Settings.GOOGLE_CLOUD_PROJECT_ID,
                Settings.DOCUMENT_AI_LOCATION,
                Settings.DOCUMENT_AI_PROCESSOR_ID
            )
            
            print("✓ Document AI initialized successfully")
        
        except Exception as e:
            print(f"✗ Document AI initialization error: {e}")
            raise
    
    def process_receipt(self, file_path: str, mime_type: str) -> Dict:
        """
        Process a receipt file and extract structured data
        
        Args:
            file_path: Path to the receipt file
            mime_type: MIME type of the file (e.g., 'image/jpeg', 'application/pdf')
        
        Returns:
            Dictionary containing extracted receipt data
        """
        try:
            # Read the file
            with open(file_path, "rb") as file:
                file_content = file.read()
            
            # Create the document object
            raw_document = documentai.RawDocument(
                content=file_content,
                mime_type=mime_type
            )
            
            # Create process request
            request = documentai.ProcessRequest(
                name=self.processor_name,
                raw_document=raw_document
            )
            
            # Process the document
            result = self.client.process_document(request=request)
            document = result.document
            
            # Extract structured data
            receipt_data = self._extract_receipt_fields(document)
            
            print(f"✓ Receipt processed successfully")
            return receipt_data
        
        except Exception as e:
            print(f"✗ Document AI processing error: {e}")
            raise
    
    def _extract_receipt_fields(self, document: documentai.Document) -> Dict:
        """
        Extract key fields from the processed document
        
        Args:
            document: Processed Document AI document
        
        Returns:
            Dictionary with extracted fields
        """
        # Initialize receipt data with defaults
        receipt_data = {
            'merchant_name': 'Unknown',
            'transaction_date': 'Unknown',
            'total_amount': 0.0,
            'currency': 'USD',
            'category': 'Uncategorized',
            'raw_text': document.text,
            'confidence': 0.0
        }
        
        # Extract entities (structured fields)
        for entity in document.entities:
            entity_type = entity.type_
            entity_value = entity.mention_text
            confidence = entity.confidence
            
            # Map entity types to our receipt fields
            if entity_type == 'merchant_name' or entity_type == 'supplier_name':
                receipt_data['merchant_name'] = entity_value
                receipt_data['confidence'] = max(receipt_data['confidence'], confidence)
            
            elif entity_type == 'receipt_date' or entity_type == 'transaction_date':
                receipt_data['transaction_date'] = entity_value
            
            elif entity_type == 'total_amount' or entity_type == 'net_amount':
                try:
                    # Extract numeric value
                    amount_str = entity_value.replace('$', '').replace(',', '').strip()
                    receipt_data['total_amount'] = float(amount_str)
                except ValueError:
                    pass
            
            elif entity_type == 'currency':
                receipt_data['currency'] = entity_value
        
        # Infer category from merchant name (simple categorization)
        receipt_data['category'] = self._infer_category(receipt_data['merchant_name'])
        
        return receipt_data
    
    def _infer_category(self, merchant_name: str) -> str:
        """
        Simple category inference based on merchant name
        
        Args:
            merchant_name: Name of the merchant
        
        Returns:
            Inferred category
        """
        merchant_lower = merchant_name.lower()
        
        # Simple keyword matching
        if any(word in merchant_lower for word in ['grocery', 'market', 'food', 'supermarket']):
            return 'Groceries'
        elif any(word in merchant_lower for word in ['restaurant', 'cafe', 'coffee', 'pizza', 'burger']):
            return 'Dining'
        elif any(word in merchant_lower for word in ['gas', 'fuel', 'shell', 'chevron', 'exxon']):
            return 'Transportation'
        elif any(word in merchant_lower for word in ['pharmacy', 'drug', 'cvs', 'walgreens']):
            return 'Healthcare'
        elif any(word in merchant_lower for word in ['clothing', 'fashion', 'shoes', 'apparel']):
            return 'Shopping'
        else:
            return 'Other'