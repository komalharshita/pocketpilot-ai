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
/* ===== Global App ===== */
body {
    background: radial-gradient(circle at top, #0b1224, #050814);
    color: #eaf6ff;
}

.gradio-container {
    max-width: 1200px !important;
    background: transparent !important;
}

/* ===== Headers ===== */
h1, h2, h3 {
    color: #eaf6ff;
    letter-spacing: 0.5px;
}

/* ===== Tabs ===== */
button[role="tab"] {
    background: transparent !important;
    color: #9bdcff !important;
    border-bottom: 2px solid transparent;
}

button[role="tab"][aria-selected="true"] {
    color: #1ec9ff !important;
    border-bottom: 2px solid #1ec9ff;
    box-shadow: 0 2px 12px rgba(30, 201, 255, 0.4);
}

/* ===== Cards / Sections ===== */
.gr-box, .gr-panel {
    background: #0b1224 !important;
    border-radius: 14px !important;
    border: 1px solid rgba(30, 201, 255, 0.25);
    box-shadow: 0 0 18px rgba(30, 201, 255, 0.08);
}

/* ===== Buttons ===== */
button.primary {
    background: linear-gradient(135deg, #1ec9ff, #2a7cff) !important;
    color: #050814 !important;
    border-radius: 12px !important;
    font-weight: 600;
    box-shadow: 0 0 18px rgba(30, 201, 255, 0.5);
}

button.primary:hover {
    box-shadow: 0 0 28px rgba(30, 201, 255, 0.75);
}

/* ===== Tables ===== */
table {
    background: #0b1224 !important;
    color: #eaf6ff !important;
}

th {
    background: #08101f !important;
    color: #4fdcff !important;
}

td {
    border-color: rgba(30, 201, 255, 0.15) !important;
}

/* ===== Inputs ===== */
input, textarea {
    background: #050814 !important;
    color: #eaf6ff !important;
    border: 1px solid rgba(30, 201, 255, 0.35) !important;
    border-radius: 10px !important;
}

input:focus, textarea:focus {
    outline: none !important;
    box-shadow: 0 0 12px rgba(30, 201, 255, 0.6);
}

/* ===== Chatbot ===== */
.gr-chatbot {
    background: #050814 !important;
    border: 1px solid rgba(30, 201, 255, 0.25);
    box-shadow: inset 0 0 20px rgba(30, 201, 255, 0.08);
}

/* ===== Footer ===== */
footer {
    display: none !important;
}
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
                    status_message,
                    summary_display,
                    category_chart,
                    time_chart,
                    merchant_chart
                ) = create_dashboard_tab(firebase_manager)

            # ================= Upload Receipt =================
            with gr.Tab("📤 Upload Receipt"):
                upload_trigger = create_receipt_upload_tab(
                    firebase_manager,
                    doc_ai_processor
                )

            # ================= Pilot Chat =================
            with gr.Tab("💬 Pilot"):
                create_chatbot_tab(
                    gemini_manager,
                    firebase_manager
                )

        # 🔁 Load dashboard on app start
        app.load(
            fn=load_dashboard,
            outputs=[
                receipts_table,
                status_message,
                summary_display,
                category_chart,
                time_chart,
                merchant_chart
            ]
        )

        # 🔁 Auto-refresh dashboard immediately after receipt upload
        upload_trigger.change(
            fn=load_dashboard,
            outputs=[
                receipts_table,
                status_message,
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
