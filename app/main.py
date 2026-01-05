# =========================
# File: main.py
# =========================
"""
PocketPilot AI - Main Application
A simple personal finance app with receipt parsing and AI chatbot
"""

import gradio as gr
from services.firebase_manager import FirebaseManager
from services.document_ai_processor import DocumentAIProcessor
from services.gemini_manager import GeminiManager
from ui.dashboard import create_dashboard_tab
from ui.receipt_upload import create_receipt_upload_tab
from ui.chatbot import create_chatbot_tab

CUSTOM_CSS = """
#summary-stats {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}
.gradio-container { max-width: 1200px !important; }
footer { display: none !important; }
"""

def create_app():

    firebase_manager = FirebaseManager()
    doc_ai_processor = DocumentAIProcessor()  # DEMO processor
    gemini_manager = GeminiManager()

    with gr.Blocks(title="PocketPilot AI - Personal Finance Assistant") as app:

        gr.Markdown("# 🚀 PocketPilot AI\n### Your Personal Finance Assistant")

        with gr.Tabs():

            with gr.Tab("📊 Dashboard"):
                load_dashboard, receipts_table, status_msg, summary_display = \
                    create_dashboard_tab(firebase_manager)

            with gr.Tab("📤 Upload Receipt"):
                create_receipt_upload_tab(firebase_manager, doc_ai_processor)

            with gr.Tab("💬 Pilot"):
                create_chatbot_tab(gemini_manager, firebase_manager)

        app.load(
            fn=load_dashboard,
            outputs=[receipts_table, status_msg, summary_display]
        )

        gr.Markdown(
            "---\n"
            "**PocketPilot AI** | "
            "_Document AI is demo-based. Gemini powers Pilot._"
        )

    return app

if __name__ == "__main__":
    create_app().launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CUSTOM_CSS,
        show_error=True
    )
