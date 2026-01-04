# services/gemini.py

import streamlit as st
import google.generativeai as genai


def init_gemini():
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in secrets")

    genai.configure(api_key=api_key)


def ask_gemini(prompt: str) -> str:
    """
    Send a single prompt to Gemini and return response.
    """

    init_gemini()

    if not prompt.strip():
        return "Please ask something."

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception as e:
        print("Gemini error:", e)
        return "Gemini is currently unavailable."
