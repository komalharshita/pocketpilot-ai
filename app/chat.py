# app/chat.py

import streamlit as st
from services.gemini_service import chat_with_gemini


def chat_page(user):
    st.subheader("Simple Gemini Chatbot")

    # Initialize chat history (UI only)
    if "simple_chat" not in st.session_state:
        st.session_state.simple_chat = []

    # Display previous messages
    for msg in st.session_state.simple_chat:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    prompt = st.chat_input("Ask anything...")

    if prompt:
        # Show user message
        st.session_state.simple_chat.append(
            {"role": "user", "content": prompt}
        )
        with st.chat_message("user"):
            st.markdown(prompt)

        # Gemini response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat_with_gemini(prompt)
                st.markdown(reply)

        # Save assistant message
        st.session_state.simple_chat.append(
            {"role": "assistant", "content": reply}
        )
