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


# Custom CSS (Gradio 6.x -> applied at launch)
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

.gradio-container {
    max-width: 1200px !important;
}

footer {
    display: none !important;
}
"""


def create_app():

    print("=" * 60)
    print("🚀 Initializing PocketPilot AI...")
    print("=" * 60)

    try:
        print("\n📦 Initializing services...")
        firebase_manager = FirebaseManager()
        doc_ai_processor = DocumentAIProcessor()
        gemini_manager = GeminiManager()

        print("\n✅ All services initialized successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        raise

    with gr.Blocks(
        title="PocketPilot AI - Personal Finance Assistant"
    ) as app:

        gr.Markdown("""
        # 🚀 PocketPilot AI
        ### Your Personal Finance Assistant
        """)

        with gr.Tabs():

            # 📊 Dashboard
            with gr.Tab("📊 Dashboard"):
                (
                    load_dashboard,
                    receipts_table,
                    status_msg,
                    summary_display
                ) = create_dashboard_tab(firebase_manager)

            # 📤 Upload Receipt
            with gr.Tab("📤 Upload Receipt"):
                create_receipt_upload_tab(firebase_manager, doc_ai_processor)

            # 💬 Chatbot
            with gr.Tab("💬 Financial Assistant"):
                create_chatbot_tab(gemini_manager, firebase_manager)

        # ✅ ONLY lifecycle hook allowed in Gradio 6.x
        app.load(
            fn=load_dashboard,
            outputs=[receipts_table, status_msg, summary_display]
        )

        gr.Markdown("""
        ---
        **PocketPilot AI** | Powered by Google Document AI & Gemini
        """)

    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CUSTOM_CSS,
        show_error=True
    )


