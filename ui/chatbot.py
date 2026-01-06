"""
Pilot AI Chatbot UI
"""

import gradio as gr
from services.gemini_manager import GeminiManager
from services.firebase_manager import FirebaseManager


def create_chatbot_tab(
    gemini_manager: GeminiManager,
    firebase_manager: FirebaseManager
):
    # NOTE:
    # gemini_manager.generate_response accepts ONLY user_message.
    # We must NOT pass receipts or modify the service.

    def respond(user_message, chat_history):
        if not user_message or user_message.strip() == "":
            return "", chat_history

        # Call Gemini correctly (no extra args)
        reply = gemini_manager.generate_response(user_message)

        # Gradio Chatbot (v4+) expects dict-based messages
        chat_history.append(
            {"role": "user", "content": user_message}
        )
        chat_history.append(
            {"role": "assistant", "content": reply}
        )

        return "", chat_history

    def clear_chat():
        return []

    with gr.Column():
        gr.Markdown("# 💬 Pilot")
        gr.Markdown("*Your AI-powered personal finance assistant*")

        chatbot = gr.Chatbot(
            label="Pilot AI Assistant",
            height=500
        )

        with gr.Row():
            message_box = gr.Textbox(
                placeholder="Ask Pilot about your finances...",
                label="Your Message",
                scale=4
            )
            send_button = gr.Button(
                "Send",
                variant="primary",
                scale=1
            )

        clear_button = gr.Button("🗑️ Clear Conversation")

        with gr.Accordion("💡 Example Questions", open=False):
            gr.Markdown("""
**General Finance:**
- How should I budget my monthly income?
- What's the best way to build an emergency fund?
- Explain the 50/30/20 rule

**About Your Receipts:**
- How much did I spend this month?
- What's my top spending category?
- Show my recent transactions
            """)

        send_button.click(
            fn=respond,
            inputs=[message_box, chatbot],
            outputs=[message_box, chatbot]
        )

        message_box.submit(
            fn=respond,
            inputs=[message_box, chatbot],
            outputs=[message_box, chatbot]
        )

        clear_button.click(
            fn=clear_chat,
            outputs=[chatbot]
        )
