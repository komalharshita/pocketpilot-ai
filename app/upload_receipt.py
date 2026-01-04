# app/upload_receipt.py

import streamlit as st
from services.document_ai import extract_receipt_text
from services.firebase import db


def upload_receipt_page(user):
    st.subheader("Upload Receipt")

    uploaded_file = st.file_uploader(
        "Upload a receipt (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if uploaded_file is None:
        return

    if st.button("Process Receipt"):
        with st.spinner("Extracting receipt text..."):
            try:
                file_bytes = uploaded_file.read()

                # Extract text using Document AI
                extracted_text = extract_receipt_text(file_bytes)

                # Save to Firestore
                db.collection("receipts").add({
                    "user_id": user["uid"],
                    "filename": uploaded_file.name,
                    "text": extracted_text,
                })

                st.success("Receipt uploaded and saved successfully!")

                st.text_area(
                    "Extracted Text (raw)",
                    extracted_text,
                    height=300
                )

            except Exception as e:
                st.error("Failed to process receipt")
                st.exception(e)
