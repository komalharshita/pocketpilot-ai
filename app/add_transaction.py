# app/add_transaction.py

import streamlit as st
from datetime import datetime
from services.transaction_service import create_transaction

def add_transaction_page(user):
    st.subheader("Add Transaction")

    with st.form("add_transaction_form"):
        t_type = st.selectbox("Type", ["expense", "income"])
        amount = st.number_input("Amount", min_value=0.0, format="%.2f")
        category = st.text_input("Category", value="General")
        date = st.date_input("Date", value=datetime.today())
        notes = st.text_area("Notes (optional)")

        submitted = st.form_submit_button("Save Transaction")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero.")
            return

        payload = {
            "user_id": user["localId"],
            "type": t_type,
            "amount": amount,
            "category": category,
            "date": datetime.combine(date, datetime.min.time()),
            "notes": notes,
            "source": "manual",
        }

        try:
            create_transaction(payload)
            st.success("Transaction added successfully.")
        except Exception as e:
            st.error(f"Failed to add transaction: {str(e)}")
