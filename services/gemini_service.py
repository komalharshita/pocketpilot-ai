# services/gemini_service.py

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set")

# Configure Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Use a fast, reliable model for chat
MODEL_NAME = "gemini-1.5-flash"

def generate_response(prompt: str) -> str:
    """
    Send a prompt to Gemini and return the response text.
    """
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    if not response or not response.text:
        return "Sorry, I couldn’t generate a response right now."

    return response.text.strip()
