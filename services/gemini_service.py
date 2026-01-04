# services/gemini_service.py

import streamlit as st
import google.generativeai as genai

# Load API key from Streamlit secrets
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in Streamlit secrets")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

<<<<<<< HEAD
# Use a currently supported model
MODEL_NAME = "gemini-2.5-pro-exp-03-25"
=======
# Stable, proven model
MODEL_NAME = "gemini-2.0-flash"
>>>>>>> 22464caa84bfcfba97c11fde73e80746f659c46f


def chat_with_gemini(prompt: str) -> str:
    if not prompt or not prompt.strip():
        return "Please ask something."

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)

        if not response or not response.text:
            return "I couldn’t generate a response right now."

        return response.text.strip()

    except Exception as e:
<<<<<<< HEAD
        # Log actual error in Streamlit Cloud logs
        print("Gemini error:", repr(e))
        return "Gemini is currently unavailable. Please try again later."
=======
        import traceback
        traceback.print_exc()
        st.error(f"Gemini error: {repr(e)}")
        raise

>>>>>>> 22464caa84bfcfba97c11fde73e80746f659c46f
