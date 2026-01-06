"""
PocketPilot AI - Main Application
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
/* PocketPilot Dark Futuristic Theme */
:root {
    --primary-accent: #1ec9ff;
    --secondary-accent: #2a7cff;
    --background: #050814;
    --card-bg: #0b1224;
    --text-color: #eaf6ff;
}

body, .gradio-container {
    background: var(--background) !important;
    color: var(--text-color) !important;
}

.gradio-container {
    max-width: 1400px !important;
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Buttons */
.gr-button {
    background: linear-gradient(135deg, var(--primary-accent), var(--secondary-accent)) !important;
    border: none !important;
    color: var(--background) !important;
    font-weight: 600 !important;
    transition: all 0.3s ease !important;
}

.gr-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 20px rgba(30, 201, 255, 0.4) !important;
}

/* Cards and Containers */
.gr-box, .gr-form, .gr-panel {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.2) !important;
    border-radius: 12px !important;
}

/* Tabs */
.gr-tab {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.2) !important;
    color: var(--text-color) !important;
}

.gr-tab.selected {
    background: linear-gradient(135deg, var(--primary-accent), var(--secondary-accent)) !important;
    color: var(--background) !important;
    font-weight: 600 !important;
}

/* Dataframe */
.gr-dataframe {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.3) !important;
}

.gr-dataframe th {
    background: linear-gradient(135deg, var(--primary-accent), var(--secondary-accent)) !important;
    color: var(--background) !important;
    font-weight: 600 !important;
}

/* Chatbot */
.gr-chatbot {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.2) !important;
}

/* Charts */
.gr-plot {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.2) !important;
    border-radius: 12px !important;
}

/* Hide Gradio footer */
footer {
    display: none !important;
}
"""

def create_app():
    print("=" * 60)
    print("🚀 Initializing PocketPilot AI...")
    print("=" * 60)

    firebase_manager = FirebaseManager()
    doc_ai_processor = DocumentAIProcessor()
    gemini_manager = GeminiManager()

    print("✅ All services initialized")
    print("=" * 60)

    with gr.Blocks(
        title="PocketPilot AI - Personal Finance Assistant",
        css=CUSTOM_CSS
    ) as app:

        gr.Markdown("""
        # PocketPilot AI
        ### *Your AI-Powered Personal Finance Assistant*
        """)

        with gr.Tabs():

            with gr.Tab("Dashboard"):
                (
                    load_dashboard,
                    receipts_table,
                    status_msg,
                    summary_display,
                    category_chart,
                    merchant_chart,
                    time_chart
                ) = create_dashboard_tab(firebase_manager)

            with gr.Tab("Upload Receipt (Demo)"):
                upload_event = create_receipt_upload_tab(
                    firebase_manager,
                    doc_ai_processor
                )

            with gr.Tab("💬 Pilot"):
                create_chatbot_tab(
                    gemini_manager,
                    firebase_manager
                )

        # Initial dashboard load
        app.load(
            fn=load_dashboard,
            outputs=[
                receipts_table,
                status_msg,
                summary_display,
                category_chart,
                merchant_chart,
                time_chart
            ]
        )

        # Auto-refresh dashboard after receipt upload
        upload_event.then(
            fn=load_dashboard,
            outputs=[
                receipts_table,
                status_msg,
                summary_display,
                category_chart,
                merchant_chart,
                time_chart
            ]
        )

        gr.Markdown("""
        ---
        **PocketPilot AI by Team CyberForge** | *Powered by Gemini AI • Google Firebase and Demo Document AI*
        """)

    return app

if __name__ == "__main__":
    create_app().launch(
        server_name=Settings.APP_HOST,
        server_port=7861,
        show_error=True,
        theme=gr.themes.Base()
    )
