import os
from google import genai


def configure_gemini():
    """
    Returns a Gemini client using the new supported SDK.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    client = genai.Client(api_key=api_key)
    return client
