"""
Gemini AI Manager for chatbot functionality
PERMANENT, stateless, Gradio-6-safe implementation
"""

from google import genai
from typing import List, Dict
from config.settings import Settings


class GeminiManager:
    def __init__(self):
        try:
            self.client = genai.Client(api_key=Settings.GEMINI_API_KEY)
            self.model = Settings.GEMINI_MODEL
            print("✓ Gemini API initialized successfully")
        except Exception as e:
            print(f"✗ Gemini initialization error: {e}")
            raise

    def generate_response(
        self,
        user_message: str,
        receipt_context: List[Dict] = None
    ) -> str:
        """
        Stateless Gemini call.
        NEVER accepts history. NEVER passes message lists.
        """

        try:
            prompt = self._build_prompt(user_message, receipt_context)

            response = self.client.models.generate_content(
                model=self.model,
                contents=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.text.strip()

        except Exception as e:
            print(f"✗ Gemini API error: {e}")
            return "Sorry — I ran into an internal error. Please try again."

    def _build_prompt(
        self,
        user_message: str,
        receipt_context: List[Dict] = None
    ) -> str:

        prompt = (
            "You are PocketPilot AI, a helpful personal finance assistant.\n"
            "Answer clearly, simply, and responsibly.\n\n"
        )

        if receipt_context:
            total = sum(r.get("total_amount", 0) for r in receipt_context)
            prompt += f"User has {len(receipt_context)} receipts. Total spent: ${total:.2f}.\n\n"

        prompt += f"User question: {user_message}"
        return prompt
