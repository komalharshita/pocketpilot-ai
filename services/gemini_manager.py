"""
Gemini Manager for Pilot
STABLE implementation using google-generativeai
"""

import google.generativeai as genai
from config.settings import Settings


class GeminiManager:
    def __init__(self):
        # Configure API key
        genai.configure(api_key=Settings.GEMINI_API_KEY)

        # Initialize model
        self.model = genai.GenerativeModel(Settings.GEMINI_MODEL)

        print("✓ Gemini initialized (google-generativeai)")

    def generate_response(self, user_message: str) -> str:
        """
        TEMP DEBUG VERSION
        Prints real Gemini error to terminal
        """

        prompt = (
            "You are Pilot, a helpful personal finance assistant.\n"
            "Answer clearly and simply.\n\n"
            f"User question: {user_message}"
        )

        try:
            response = self.model.generate_content(prompt)

            print("✅ RAW GEMINI RESPONSE:", response)

            if not response or not response.text:
                return "No text returned from Gemini."

            return response.text.strip()

        except Exception as e:
            print("🔥🔥🔥 REAL GEMINI ERROR 🔥🔥🔥")
            print(type(e))
            print(e)
            print("🔥🔥🔥 END ERROR 🔥🔥🔥")

            return "Gemini API failed. Check terminal logs."
