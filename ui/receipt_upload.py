"""
Receipt Upload UI component
Handles file upload and Document AI processing
"""

import gradio as gr
import os
from services.firebase_manager import FirebaseManager
from services.document_ai_processor import DocumentAIProcessor
from utils.helpers import (
    validate_file, 
    get_mime_type, 
    format_currency,
    create_success_message,
    create_error_message
)

def create_receipt_upload_tab(firebase_manager: FirebaseManager, doc_ai_processor: DocumentAIProcessor):
    """
    Create the receipt upload tab interface
    
    Args:
        firebase_manager: Initialized FirebaseManager instance
        doc_ai_processor: Initialized DocumentAIProcessor instance
    
    Returns:
        Gradio column component
    """
    
    def process_receipt(file):
        """
        Process uploaded receipt file
        
        Args:
            file: Gradio file upload object
        
        Returns:
            Tuple of (status_message, result_json)
        """
        try:
            if file is None:
                return create_error_message("No file uploaded"), ""
            
            # Get file path from Gradio file object
            file_path = file.name if hasattr(file, 'name') else str(file)
            file_name = os.path.basename(file_path)
            
            # Validate file
            is_valid, validation_msg = validate_file(file_path)
            if not is_valid:
                return create_error_message(validation_msg), ""
            
            # Get MIME type
            mime_type = get_mime_type(file_path)
            
            # Process with Document AI
            status_msg = "📄 Processing receipt with Document AI..."
            receipt_data = doc_ai_processor.process_receipt(file_path, mime_type)
            
            # Upload file to Firebase Storage
            status_msg = "☁️ Uploading file to Firebase Storage..."
            storage_url = firebase_manager.upload_receipt_file(file_path, file_name)
            receipt_data['storage_url'] = storage_url
            receipt_data['original_filename'] = file_name
            
            # Save to Firestore
            status_msg = "💾 Saving receipt data to Firestore..."
            doc_id = firebase_manager.save_receipt_data(receipt_data)
            receipt_data['id'] = doc_id
            
            # Format result for display
            result_text = f"""
### ✅ Receipt Processed Successfully!

**Document ID:** {doc_id}

**Extracted Information:**
- **Merchant:** {receipt_data.get('merchant_name', 'Unknown')}
- **Date:** {receipt_data.get('transaction_date', 'Unknown')}
- **Amount:** {format_currency(receipt_data.get('total_amount', 0), receipt_data.get('currency', 'USD'))}
- **Category:** {receipt_data.get('category', 'Uncategorized')}
- **Confidence:** {receipt_data.get('confidence', 0):.2%}

The receipt has been saved to your database. You can view it in the Dashboard tab.
"""
            
            return create_success_message(f"Receipt '{file_name}' processed successfully!"), result_text
        
        except Exception as e:
            error_msg = f"Error processing receipt: {str(e)}"
            return create_error_message(error_msg), ""
    
    with gr.Column() as upload_tab:
        gr.Markdown("# 📤 Upload Receipt")
        gr.Markdown("Upload a receipt image (JPEG, PNG) or PDF file to extract data automatically")
        
        # File upload
        file_input = gr.File(
            label="Select Receipt File",
            file_types=[".jpg", ".jpeg", ".png", ".pdf"],
            type="filepath"
        )
        
        # Upload button
        upload_btn = gr.Button("🚀 Process Receipt", variant="primary", size="lg")
        
        # Status message
        status_msg = gr.Markdown("")
        
        # Results display
        results_display = gr.Markdown("", label="Extraction Results")
        
        # Instructions
        with gr.Accordion("ℹ️ How it works", open=False):
            gr.Markdown("""
### Receipt Processing Pipeline

1. **Upload File**: Select a receipt image or PDF
2. **Document AI**: Google Document AI extracts structured data
3. **Storage**: File is uploaded to Firebase Storage
4. **Database**: Extracted data is saved to Firestore
5. **Dashboard**: View your receipt in the Dashboard tab

### Supported Formats
- Images: JPEG, PNG
- Documents: PDF
- Max file size: 10MB

### Extracted Data
- Merchant name
- Transaction date
- Total amount
- Currency
- Category (auto-detected)
            """)
        
        # Connect upload button
        upload_btn.click(
            fn=process_receipt,
            inputs=[file_input],
            outputs=[status_msg, results_display]
        )
    
    return upload_tab