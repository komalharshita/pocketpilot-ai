# services/gemini_service.py

import os
import streamlit as st
from google import genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-pro"


def generate_response(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        if not response or not response.text:
            return "I couldn't generate a response. Try again."

        return response.text.strip()

    except Exception:
        return "Sorry, I'm having trouble responding right now."
