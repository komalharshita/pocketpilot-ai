# =========================
# File: main.py
# =========================
"""
PocketPilot AI - Main Application
Wires UI + Services together and launches the Gradio app
"""

import gradio as gr
from services.firebase_manager import FirebaseManager
from services.document_ai_processor import DocumentAIProcessor
from services.gemini_manager import GeminiManager
from ui.dashboard import create_dashboard_tab
from ui.receipt_upload import create_receipt_upload_tab
from ui.chatbot import create_chatbot_tab
from config.settings import Settings

CUSTOM_CSS = """
.gradio-container { max-width: 1200px !important; }
footer { display: none !important; }
"""

def create_app():
    print("=" * 60)
    print("🚀 Initializing PocketPilot AI...")
    print("=" * 60)

    # Initialize services
    firebase_manager = FirebaseManager()
    doc_ai_processor = DocumentAIProcessor()  # demo / mocked
    gemini_manager = GeminiManager()

    with gr.Blocks(
        title="PocketPilot AI - Personal Finance Assistant"
    ) as app:

        gr.Markdown("# 🚀 PocketPilot AI\n### Your Personal Finance Assistant")

        with gr.Tabs():

            # ================= Dashboard =================
            with gr.Tab("📊 Dashboard"):
                (
                    load_dashboard,
                    receipts_table,
                    status_msg,
                    summary_display,
                    category_chart,
                    time_chart,
                    merchant_chart
                ) = create_dashboard_tab(firebase_manager)

            # ================= Upload Receipt =================
            with gr.Tab("📤 Upload Receipt"):
                create_receipt_upload_tab(
                    firebase_manager,
                    doc_ai_processor
                )

            # ================= Pilot Chat =================
            with gr.Tab("💬 Pilot"):
                create_chatbot_tab(
                    gemini_manager,
                    firebase_manager
                )

        # Auto-load dashboard on app start
        app.load(
            fn=load_dashboard,
            outputs=[
                receipts_table,
                status_msg,
                summary_display,
                category_chart,
                time_chart,
                merchant_chart
            ]
        )

        gr.Markdown(
            "---\n"
            "**PocketPilot AI** | _Document AI is demo-based. Pilot is powered by Gemini._"
        )

    return app


if __name__ == "__main__":
    create_app().launch(
        server_name=Settings.APP_HOST,
        server_port=7861,
        css=CUSTOM_CSS,
        show_error=True
    )
