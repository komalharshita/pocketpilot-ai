# =========================
# File: services/gemini_manager.py
# =========================
"""
Gemini AI Manager for Pilot (Chatbot)
Stateless and Gradio-safe
"""

from google import genai
from typing import List, Dict
from config.settings import Settings

class GeminiManager:
    def __init__(self):
        self.client = genai.Client(api_key=Settings.GEMINI_API_KEY)
        self.model = Settings.GEMINI_MODEL

    def generate_response(
        self,
        user_message: str,
        receipt_context: List[Dict] = None
    ) -> str:

        prompt = (
            "You are Pilot, a helpful personal finance assistant.\n"
            "Answer clearly, simply, and responsibly.\n\n"
        )

        if receipt_context:
            total = sum(r.get("total_amount", 0) for r in receipt_context)
            prompt += (
                f"User has {len(receipt_context)} receipts. "
                f"Total spent: ${total:.2f}.\n\n"
            )

        prompt += f"User question: {user_message}"

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=[{"role": "user", "content": prompt}]
            )
            return response.text.strip()
        except Exception:
            return "Sorry — Pilot ran into an error. Please try again."
