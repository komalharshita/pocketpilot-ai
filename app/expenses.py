# app/expenses.py

import streamlit as st
from services.firebase import db


def expenses_page(user):
    st.subheader("My Expenses")

    user_id = user["uid"]

    try:
        receipts_ref = (
            db.collection("receipts")
            .where("user_id", "==", user_id)
            .stream()
        )

        receipts = list(receipts_ref)

        if not receipts:
            st.info("No receipts uploaded yet.")
            return

        for i, doc in enumerate(receipts, start=1):
            data = doc.to_dict()

            with st.expander(f"Receipt {i}: {data.get('filename', 'Unknown')}"):
                st.text_area(
                    "Extracted Text",
                    data.get("text", ""),
                    height=250
                )

    except Exception as e:
        st.error("Failed to load expenses")
        st.exception(e)
