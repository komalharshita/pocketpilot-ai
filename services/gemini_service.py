"""
Gemini API Integration for PocketPilot AI
Simple, stable chatbot with predefined prompts
Uses google.genai (official, supported SDK)
"""

import os
from typing import Optional
from google import genai


class GeminiClient:
    """
    Minimal Gemini client for PocketPilot AI
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found")

        # ✅ NEW SDK (official)
        self.client = genai.Client(api_key=self.api_key)

        # ✅ Supported, stable model - consistent across all files
        self.model = "gemini-1.5-flash"

    def ask(self, prompt: str) -> str:
        """
        Send a simple prompt to Gemini and return response
        """
        if not prompt or not prompt.strip():
            return "Please ask a valid question."

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            if response and hasattr(response, 'text'):
                return response.text.strip()

            return "I couldn't generate a response."

        except Exception as e:
            return f"⚠️ Gemini is currently unavailable: {str(e)}"


# ------------------------------------------------------------------
# Built-in prompts (ONLY these are intended to be used by the UI)
# ------------------------------------------------------------------

BUILT_IN_PROMPTS = {
    "summary": "Give me a simple summary of my expenses in an easy-to-understand way.",
    "tips": "Give me 5 simple tips to reduce my monthly expenses as a student.",
    "budget": "Help me create a basic monthly budget using simple language."
}


# ------------------------------------------------------------------
# Helper functions (safe & simple)
# ------------------------------------------------------------------

def get_quick_insight(prompt_key: str, api_key: Optional[str] = None) -> str:
    """
    Get Gemini response using one of the built-in prompts

    Args:
        prompt_key: one of ['summary', 'tips', 'budget']
        api_key: optional Gemini API key

    Returns:
        Gemini response text
    """
    if prompt_key not in BUILT_IN_PROMPTS:
        return "Invalid prompt selection."

    try:
        client = GeminiClient(api_key)
        return client.ask(BUILT_IN_PROMPTS[prompt_key])
    except Exception as e:
        return f"⚠️ Could not connect to Gemini API: {str(e)}"