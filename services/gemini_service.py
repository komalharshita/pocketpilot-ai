# services/gemini_service.py

import os
import streamlit as st
from google import genai

# ------------------------------------------------------------------
# Load Gemini API key
# ------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment or Streamlit secrets")

# ------------------------------------------------------------------
# Initialize Gemini client (AI Studio / API-key based)
# ------------------------------------------------------------------
client = genai.Client(api_key=GEMINI_API_KEY)

# Use the most stable, universally available model
MODEL_NAME = "models/gemini-1.0-pro"


def generate_response(prompt: str) -> str:
    """
    Generate a response from Gemini.
    This function is Streamlit-safe and will not crash the app.
    """

    if not isinstance(prompt, str) or not prompt.strip():
        return "Please ask a valid question."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=[prompt]   # IMPORTANT: contents must be a list
        )

        if response is None:
            return "I couldn’t generate a response right now."

        # Defensive extraction (SDK-safe)
        text = getattr(response, "text", None)

        if not text:
            return "I couldn’t generate a response right now."

        return text.strip()

    except Exception as e:
        # Log the real error to server logs
        print("Gemini error:", repr(e))

        # User-friendly fallback
        return "Sorry, I’m having trouble responding right now."
