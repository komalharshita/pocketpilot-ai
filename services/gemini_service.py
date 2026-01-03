# services/gemini_service.py

import os
import streamlit as st
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-pro"  


def generate_response(prompt: str) -> str:
    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        if not response or not response.text:
            return "I couldn't generate a response. Try asking in a different way."

        return response.text.strip()

    except Exception as e:
        # Prevent app crash & show friendly message
        return (
            "Sorry, I’m having trouble answering right now. "
            "Please try again in a moment."
        )
