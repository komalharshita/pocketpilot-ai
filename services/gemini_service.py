# services/gemini_service.py

import os
import streamlit as st
from google import genai

# Load API key safely
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

# Initialize Gemini client (NEW SDK)
client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "models/gemini-1.0-pro"

def generate_response(prompt: str) -> str:
    if not prompt or not prompt.strip():
        return "Please ask a valid question."

    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            return "I couldn’t generate a response right now."

        return response.text.strip()

    except Exception as e:
        # Log for debugging
        print("Gemini error:", e)
        return "Sorry, I’m having trouble responding right now."
