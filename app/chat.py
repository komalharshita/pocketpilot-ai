# app/chat.py

import streamlit as st
from services.analytics_data import get_transactions_df
from services.analytics_metrics import (
    compute_basic_metrics,
    compute_category_totals,
    compute_monthly_totals,
    compute_month_over_month_change,
)
from services.ai_summary import build_financial_summary
from services.ai_prompt import build_prompt
from services.gemini_service import generate_response


def chat_page(user):
    st.subheader("Chat with Pilot")

    user_id = user["localId"]

    # Session state for chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Display chat history
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # User input
    user_query = st.chat_input("Ask about your spending...")

    if user_query:
        # Show user message
        st.session_state.chat_history.append(
            {"role": "user", "content": user_query}
        )

        with st.chat_message("user"):
            st.markdown(user_query)

        # Prepare analytics context
        df = get_transactions_df(user_id)
        basic = compute_basic_metrics(df)
        category = compute_category_totals(df)
        monthly = compute_monthly_totals(df)
        mom = compute_month_over_month_change(monthly)

        summary = build_financial_summary(
            basic, category, monthly, mom
        )

        prompt = build_prompt(summary, user_query)

        # Gemini response
        with st.chat_message("assistant"):
            with st.spinner("Pilot is thinking..."):
                response = generate_response(prompt)
                st.markdown(response)

        # Save assistant response
        st.session_state.chat_history.append(
            {"role": "assistant", "content": response}
        )
