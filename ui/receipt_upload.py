"""
Receipt Upload UI
Uses DEMO Document AI (free-tier safe)
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


def create_receipt_upload_tab(
    firebase_manager: FirebaseManager,
    doc_ai_processor: DocumentAIProcessor
):
    """
    Receipt upload tab
    NOTE:
    - Does NOT handle dashboard refresh itself
    - Returns the upload event so main.py can chain .then(load_dashboard)
    """

    def process_receipt(file):
        try:
            if not file:
                return create_error_message("No file uploaded"), ""

            file_path = file
            file_name = os.path.basename(file_path)

            is_valid, msg = validate_file(file_path)
            if not is_valid:
                return create_error_message(msg), ""

            # DEMO Document AI processing (service untouched)
            receipt_data = doc_ai_processor.process_receipt(
                file_path,
                get_mime_type(file_path)
            )

            receipt_data["original_filename"] = file_name
            firebase_manager.save_receipt_data(receipt_data)

            result_text = f"""
### ✅ Receipt Processed Successfully

**Merchant:** {receipt_data.get('merchant_name', 'Unknown')}  
**Date:** {receipt_data.get('transaction_date', 'Unknown')}  
**Amount:** {format_currency(receipt_data.get('total_amount', 0))}  
**Category:** {receipt_data.get('category', 'Other')}  
**Confidence:** {receipt_data.get('confidence', 0):.0%}

---

ℹ️ *Document AI is demo-based for free-tier compatibility. Real API integration available.*
"""
            return (
                create_success_message(f"Receipt '{file_name}' processed"),
                result_text
            )

        except Exception as e:
            return create_error_message(str(e)), ""

    with gr.Column():
        gr.Markdown("# Upload Receipt")
        gr.Markdown("*Upload receipt images or PDFs for automatic data extraction*")

        file_input = gr.File(
            label="Select Receipt File (JPG, PNG, PDF)",
            type="filepath"
        )

        upload_button = gr.Button(
            "🚀 Process Receipt",
            variant="primary"
        )

        status_message = gr.Markdown("")
        result_display = gr.Markdown("")

        upload_event = upload_button.click(
            fn=process_receipt,
            inputs=[file_input],
            outputs=[status_message, result_display]
        )

    return upload_event
