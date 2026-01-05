# =========================
# File: ui/receipt_upload.py
# =========================
"""
Receipt Upload UI (Demo Document AI)
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

    def process_receipt(file):
        if not file:
            return create_error_message("No file uploaded"), ""

        file_path = file
        valid, msg = validate_file(file_path)
        if not valid:
            return create_error_message(msg), ""

        receipt_data = doc_ai_processor.process_receipt(
            file_path, get_mime_type(file_path)
        )

        receipt_data["original_filename"] = os.path.basename(file_path)
        doc_id = firebase_manager.save_receipt_data(receipt_data)

        result = f"""
### ✅ Receipt Processed (Demo Mode)

**Merchant:** {receipt_data['merchant_name']}
**Amount:** {format_currency(receipt_data['total_amount'])}
**Category:** {receipt_data['category']}

ℹ️ Document AI is not available in the free tier.
You can integrate the real API on your own.
"""

        return create_success_message("Receipt processed (demo)"), result

    with gr.Column():
        gr.Markdown("# 📤 Upload Receipt")
        gr.Markdown(
            "_Document AI is demo-based. "
            "Real API requires paid Google Cloud._"
        )

        file_input = gr.File(type="filepath")
        btn = gr.Button("Process Receipt", variant="primary")

        status = gr.Markdown()
        output = gr.Markdown()

        btn.click(process_receipt, [file_input], [status, output])
