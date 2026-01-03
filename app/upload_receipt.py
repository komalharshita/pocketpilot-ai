# app/upload_receipt.py

import streamlit as st
from services.document_ai_service import parse_receipt
from services.receipt_extractor import extract_receipt_fields

def upload_receipt_page(user):
    st.subheader("Upload Receipt")

    uploaded_file = st.file_uploader(
        "Upload a receipt (JPG, PNG, PDF)",
        type=["jpg", "jpeg", "png", "pdf"],
    )

    if not uploaded_file:
        st.info("Upload a receipt to extract expense details.")
        return

    # Determine MIME type
    mime_type = uploaded_file.type
    file_bytes = uploaded_file.read()

    with st.spinner("Processing receipt with Document AI..."):
        try:
            document = parse_receipt(file_bytes, mime_type)
        except Exception as e:
            st.error(f"Failed to process receipt: {str(e)}")
            return

       # Normalize extracted data
    data = extract_receipt_fields(document)

    st.subheader("Extracted Receipt Summary")

    st.write({
        "Amount": data["amount"],
        "Date": data["date"].strftime("%Y-%m-%d") if data["date"] else None,
        "Merchant": data["merchant"],
        "Confidence": data["confidence"],
    })


    if not document.entities:
        st.warning("No entities detected. Try a clearer receipt.")
        return

    extracted = []
    for ent in document.entities:
        extracted.append(
            {
                "type": ent.type_,
                "value": ent.mention_text,
                "confidence": round(ent.confidence, 2),
            }
        )

    st.dataframe(extracted, use_container_width=True)

    st.caption(
        "You’ll be able to review, edit, and save this as a transaction in the next step."
    )
