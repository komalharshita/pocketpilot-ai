import os
from google import genai
from services.expense_manager import load_expenses


def get_gemini_client():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set")

    return genai.Client(api_key=api_key)


def generate_chat_response(user_query: str) -> str:
    client = get_gemini_client()
    df = load_expenses()

    if df.empty:
        expense_context = "The user has no expenses recorded yet."
    else:
        total_spent = df[df["type"] == "expense"]["amount"].sum()
        category_spending = (
            df[df["type"] == "expense"]
            .groupby("category")["amount"]
            .sum()
            .to_dict()
        )

        expense_context = f"""
        Total spent: {total_spent}
        Category-wise spending: {category_spending}
        """

    prompt = f"""
You are PocketPilot AI, a friendly personal finance assistant for students.

User expense data:
{expense_context}

User question:
{user_query}

Respond in simple, clear, practical language.
Avoid technical jargon.
"""

    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt
    )

    return response.text
