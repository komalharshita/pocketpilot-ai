from services.gemini_service import generate_response

if __name__ == "__main__":
    prompt = "Explain what an expense tracker does in one sentence."
    response = generate_response(prompt)
    print("Gemini Response:\n", response)
