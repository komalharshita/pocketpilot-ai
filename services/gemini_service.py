# services/gemini_service.py

import streamlit as st
import google.generativeai as genai

# ------------------------------------------------------------------
# Configure Gemini using Streamlit secrets
# ------------------------------------------------------------------
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in Streamlit secrets")

genai.configure(api_key=GEMINI_API_KEY)

# Stable, proven model
MODEL_NAME = "gemini-pro"


def generate_response(prompt: str, history: list | None = None) -> str:
    """
    Generate a response using Gemini Pro with chat history.
    This uses the same logic as the known-working reference chatbot.
    """

    if not prompt or not prompt.strip():
        return "Please ask a valid question."

    if history is None:
        history = []

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        chat = model.start_chat(history=history)

        response = chat.send_message(prompt)

        if not response or not response.text:
            return "I couldn’t generate a response right now."

        return response.text.strip()

    except Exception as e:
        # Log for debugging (visible in Streamlit Cloud logs)
        print("Gemini error:", e)
        return "Sorry, I’m having trouble responding right now."
