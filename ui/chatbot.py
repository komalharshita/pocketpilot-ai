# =========================
# File: ui/chatbot.py
# =========================
"""
Pilot Chatbot UI
"""

import gradio as gr
from services.gemini_manager import GeminiManager
from services.firebase_manager import FirebaseManager

def create_chatbot_tab(
    gemini_manager: GeminiManager,
    firebase_manager: FirebaseManager
):

    def respond(message, chat_history):
        if not message.strip():
            return "", chat_history

        receipts = firebase_manager.get_all_receipts()
        reply = gemini_manager.generate_response(message, receipts)
        chat_history.append((message, reply))
        return "", chat_history

    def clear_chat():
        return []

    with gr.Column():
        gr.Markdown("# 💬 Pilot")
        gr.Markdown("Your personal finance assistant")

        chatbot = gr.Chatbot(label="Pilot", height=500)

        with gr.Row():
            msg = gr.Textbox(
                label="Your Message",
                placeholder="Ask Pilot about your spending..."
            )
            send = gr.Button("Send", variant="primary")

        clear = gr.Button("🗑️ Clear Conversation")

        send.click(respond, [msg, chatbot], [msg, chatbot])
        msg.submit(respond, [msg, chatbot], [msg, chatbot])
        clear.click(clear_chat, outputs=[chatbot])
