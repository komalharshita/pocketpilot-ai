import os
from google import genai

# ---------------------------
# Load API Key
# ---------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY is not set in environment variables")

# ---------------------------
# Create GenAI Client (NEW SDK WAY)
# ---------------------------
client = genai.Client(api_key=GEMINI_API_KEY)


# ---------------------------
# Chatbot Logic
# ---------------------------
def chat_with_pocketpilot(user_input: str) -> str:
    """
    Always returns a string.
    Safe for Gradio / FastAPI / Spaces.
    """
    try:
        if not user_input or not user_input.strip():
            return "Please enter a message."

        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=user_input
        )

        # ✅ Correct response extraction
        if response and response.text:
            return response.text.strip()

        return "Sorry, I couldn't generate a response."

    except Exception as e:
        # NEVER let errors escape the UI layer
        return f"⚠️ Gemini error: {str(e)}"
