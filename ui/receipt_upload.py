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
    doc_ai_processor: DocumentAIProcessor,
    refresh_dashboard_fn
):
    """Receipt upload tab with auto-refresh"""
    
    def process_receipt(file, current_trigger):
        try:
            if not file:
                return create_error_message("No file uploaded"), "", current_trigger
            
            file_path = file
            file_name = os.path.basename(file_path)
            
            is_valid, msg = validate_file(file_path)
            if not is_valid:
                return create_error_message(msg), "", current_trigger
            
            receipt_data = doc_ai_processor.process_receipt(
                file_path,
                get_mime_type(file_path)
            )
            
            receipt_data["original_filename"] = file_name
            doc_id = firebase_manager.save_receipt_data(receipt_data)
            
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
            
            new_trigger = current_trigger + 1
            
            return (
                create_success_message(f"Receipt '{file_name}' processed"),
                result_text,
                new_trigger
            )
            
        except Exception as e:
            return create_error_message(str(e)), "", current_trigger
    
    with gr.Column():
        gr.Markdown("# 📤 Upload Receipt")
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
        
        upload_button.click(
            fn=process_receipt,
            inputs=[file_input, gr.State(value=0)],
            outputs=[status_message, result_display, gr.State()]
        ).then(
            fn=refresh_dashboard_fn,
            inputs=[gr.State()],
            outputs=[
                gr.Dataframe(),
                gr.Markdown(),
                gr.Markdown(),
                gr.BarPlot(),
                gr.LinePlot(),
                gr.BarPlot(),
                gr.State()
            ]
        )