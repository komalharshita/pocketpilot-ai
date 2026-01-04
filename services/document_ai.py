# services/document_ai.py

import streamlit as st
from google.cloud import documentai_v1 as documentai


def extract_receipt_text(file_bytes: bytes) -> str:
    """
    Sends a receipt to Document AI and returns extracted text.
    """

    project_id = st.secrets["DOCUMENT_AI_PROJECT_ID"]
    location = st.secrets["DOCUMENT_AI_LOCATION"]
    processor_id = st.secrets["DOCUMENT_AI_PROCESSOR_ID"]

    client = documentai.DocumentProcessorServiceClient()

    name = client.processor_path(project_id, location, processor_id)

    document = documentai.RawDocument(
        content=file_bytes,
        mime_type="application/pdf"
    )

    request = documentai.ProcessRequest(
        name=name,
        raw_document=document
    )

    result = client.process_document(request=request)

    return result.document.text
