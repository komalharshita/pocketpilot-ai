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

.user-message {
    background: rgba(30, 201, 255, 0.15) !important;
    border-left: 3px solid var(--primary-accent) !important;
}

.bot-message {
    background: rgba(42, 124, 255, 0.15) !important;
    border-left: 3px solid var(--secondary-accent) !important;
}

/* Charts */
.gr-plot {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.2) !important;
    border-radius: 12px !important;
}

/* Markdown */
.gr-markdown h1, .gr-markdown h2, .gr-markdown h3 {
    color: var(--primary-accent) !important;
}

/* Textbox */
.gr-textbox input, .gr-textbox textarea {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.3) !important;
    color: var(--text-color) !important;
}

.gr-textbox input:focus, .gr-textbox textarea:focus {
    border-color: var(--primary-accent) !important;
    box-shadow: 0 0 10px rgba(30, 201, 255, 0.3) !important;
}

/* File Upload */
.gr-file {
    background: var(--card-bg) !important;
    border: 2px dashed rgba(30, 201, 255, 0.4) !important;
    border-radius: 12px !important;
}

/* Hide Gradio footer */
footer {
    display: none !important;
}

/* Accordion */
.gr-accordion {
    background: var(--card-bg) !important;
    border: 1px solid rgba(30, 201, 255, 0.2) !important;
}

/* Status messages */
.gr-markdown code {
    background: rgba(30, 201, 255, 0.1) !important;
    color: var(--primary-accent) !important;
    padding: 2px 6px !important;
    border-radius: 4px !important;
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
    
    with gr.Blocks(title="PocketPilot AI - Personal Finance Assistant") as app:
        
        gr.Markdown("""
        # 🚀 PocketPilot AI
        ### *Your AI-Powered Personal Finance Assistant*
        """)
        
        dashboard_outputs = None
        
        with gr.Tabs():
            
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
                
                dashboard_outputs = [
                    receipts_table,
                    status_msg,
                    summary_display,
                    category_chart,
                    time_chart,
                    merchant_chart
                ]
            
            with gr.Tab("📤 Upload Receipt"):
                create_receipt_upload_tab(
                    firebase_manager,
                    doc_ai_processor,
                    load_dashboard
                )
            
            with gr.Tab("💬 Pilot"):
                create_chatbot_tab(
                    gemini_manager,
                    firebase_manager
                )
        
        app.load(
            fn=load_dashboard,
            inputs=[gr.State(value=0)],
            outputs=dashboard_outputs + [gr.State()]
        )
        
        gr.Markdown("""
        ---
        **PocketPilot AI** | *Powered by Gemini AI • Demo Document AI*
        """)
    
    return app


if __name__ == "__main__":
    create_app().launch(
        server_name=Settings.APP_HOST,
        server_port=7861,
        show_error=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Base()
    )

