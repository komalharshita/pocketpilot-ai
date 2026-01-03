# services/gemini_service.py

import os
import streamlit as st
import google.generativeai as genai

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or st.secrets["GEMINI_API_KEY"]

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

genai.configure(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-1.5-flash"

def generate_response(prompt: str) -> str:
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    if not response or not response.text:
        return "Sorry, I couldn’t generate a response right now."

    return response.text.strip()
