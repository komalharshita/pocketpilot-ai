# app/upload_receipt.py

import streamlit as st
from services.document_ai_service import parse_receipt
from services.receipt_extractor import extract_receipt_fields
from services.receipt_service import save_receipt_and_transaction


def upload_receipt_page(user):
    st.subheader("Upload Receipt")

    uploaded_file = st.file_uploader(
        "Upload a receipt (JPG, PNG, PDF)",
        type=["jpg", "jpeg", "png", "pdf"],
    )

    if not uploaded_file:
        st.info("Upload a receipt to extract expense details.")
        return

    mime_type = uploaded_file.type
    file_bytes = uploaded_file.read()

    with st.spinner("Processing receipt with Document AI..."):
        try:
            document = parse_receipt(file_bytes, mime_type)
        except Exception as e:
            st.error(f"Failed to process receipt: {str(e)}")
            return

    data = extract_receipt_fields(document)

    st.subheader("Review & Confirm Receipt")

    with st.form("receipt_review_form"):
        amount = st.number_input(
            "Amount",
            value=data["amount"] or 0.0,
            format="%.2f"
        )

        date = st.date_input(
            "Date",
            value=data["date"].date() if data["date"] else None
        )

        merchant = st.text_input(
            "Merchant",
            value=data["merchant"] or ""
        )

        category = st.text_input("Category", value="General")

        submitted = st.form_submit_button("Save as Expense")

    if submitted:
        if amount <= 0:
            st.error("Amount must be greater than zero.")
            return

        receipt_data = {
            "amount": amount,
            "date": data["date"],
            "merchant": merchant,
            "confidence": data["confidence"],
        }

        save_receipt_and_transaction(
            user_id=user["localId"],
            receipt_data=receipt_data,
            category=category,
        )

        st.success("Receipt saved and expense created successfully.")
        st.experimental_rerun()
