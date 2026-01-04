# app/chat.py

import streamlit as st
from services.firebase import db
from services.gemini import ask_gemini


def chat_page(user):
    st.subheader("Ask Gemini About Your Expenses")

    user_id = user["uid"]

    # Fetch user's receipt texts
    receipts_ref = (
        db.collection("receipts")
        .where("user_id", "==", user_id)
        .stream()
    )

    receipt_texts = []
    for doc in receipts_ref:
        data = doc.to_dict()
        text = data.get("text", "")
        if text:
            receipt_texts.append(text)

    if not receipt_texts:
        st.info("Upload receipts first to chat with Gemini.")
        return

    # Combine receipt text into context
    context = "\n\n".join(receipt_texts[:3])  # limit context to avoid quota issues

    user_question = st.text_input("Ask a question about your receipts")

    if st.button("Ask Gemini"):
        if not user_question.strip():
            st.warning("Please enter a question.")
            return

        prompt = f"""
You are a helpful personal finance assistant.

Here is raw receipt text from a user's expenses:
{context}

User question:
{user_question}
"""

        with st.spinner("Gemini is thinking..."):
            answer = ask_gemini(prompt)

        st.markdown("### Gemini's Answer")
        st.write(answer)
