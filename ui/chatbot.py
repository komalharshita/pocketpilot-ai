import gradio as gr
from services.gemini_manager import GeminiManager
from services.firebase_manager import FirebaseManager


def create_chatbot_tab(
    gemini_manager: GeminiManager,
    firebase_manager: FirebaseManager
):

    def respond(user_message, chat_history):
        if not user_message or user_message.strip() == "":
            return "", chat_history

        reply = gemini_manager.generate_response(user_message)

        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": reply})

        return "", chat_history

    def clear_chat():
        return []

    with gr.Column():
        gr.Markdown("# 💬 Pilot")
        gr.Markdown("Your personal finance assistant")

        chatbot = gr.Chatbot(label="Pilot", height=500)

        with gr.Row():
            message_box = gr.Textbox(
                placeholder="Ask Pilot about your finances...",
                label="Your Message"
            )
            send_button = gr.Button("Send", variant="primary")

        clear_button = gr.Button("🗑️ Clear Conversation")

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
