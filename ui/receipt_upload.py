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
    Receipt upload tab with demo Document AI
    Returns a trigger signal to refresh dashboard after upload
    """

    upload_trigger = gr.State(False)  # 🔑 used for auto-refresh

    def process_receipt(file):
        try:
            if not file:
                return create_error_message("No file uploaded"), "", False

            file_path = file
            file_name = os.path.basename(file_path)

            is_valid, msg = validate_file(file_path)
            if not is_valid:
                return create_error_message(msg), "", False

            # DEMO Document AI processing
            receipt_data = doc_ai_processor.process_receipt(
                file_path,
                get_mime_type(file_path)
            )

            receipt_data["original_filename"] = file_name

            firebase_manager.save_receipt_data(receipt_data)

            result_text = f"""
### ✅ Receipt Processed (Demo Mode)

**Merchant:** {receipt_data.get('merchant_name')}
**Date:** {receipt_data.get('transaction_date')}
**Amount:** {format_currency(receipt_data.get('total_amount'))}
**Category:** {receipt_data.get('category')}
**Confidence:** {receipt_data.get('confidence'):.0%}

ℹ️ **Document AI is not available in the free tier.**
Users can integrate the real API on their own.
"""

            return (
                create_success_message(f"Receipt '{file_name}' processed successfully"),
                result_text,
                True  # 🔥 trigger dashboard refresh
            )

        except Exception as e:
            return create_error_message(str(e)), "", False

    with gr.Column():
        gr.Markdown("# 📤 Upload Receipt")
        gr.Markdown(
            "_Document AI is demo-based. "
            "Real Google Document AI requires a paid plan._"
        )

        file_input = gr.File(
            label="Upload receipt (JPG, PNG, PDF)",
            type="filepath"
        )

        upload_button = gr.Button(
            "🚀 Process Receipt",
            variant="primary"
        )

        status_message = gr.Markdown("")
        result_display = gr.Markdown("")

        upload_button.click(
            fn=process_receipt,
            inputs=[file_input],
            outputs=[status_message, result_display, upload_trigger]
        )

    return upload_trigger
