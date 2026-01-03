# services/document_ai_service.py

import json
import os
import streamlit as st
from google.cloud import documentai_v1 as documentai

PROJECT_ID = os.getenv("DOCUMENT_AI_PROJECT_ID")
LOCATION = os.getenv("DOCUMENT_AI_LOCATION")
PROCESSOR_ID = os.getenv("DOCUMENT_AI_PROCESSOR_ID")

if not all([PROJECT_ID, LOCATION, PROCESSOR_ID]):
    raise ValueError("Document AI environment variables not set")

def get_document_ai_client():
    """
    Create Document AI client using Streamlit secrets.
    """
    creds_dict = json.loads(
        st.secrets["FIREBASE_SERVICE_ACCOUNT_JSON"]
    )

    return documentai.DocumentProcessorServiceClient.from_service_account_info(
        creds_dict
    )

def parse_receipt(file_bytes: bytes, mime_type: str):
    client = get_document_ai_client()

    processor_name = client.processor_path(
        PROJECT_ID, LOCATION, PROCESSOR_ID
    )

    document = documentai.RawDocument(
        content=file_bytes,
        mime_type=mime_type,
    )

    request = documentai.ProcessRequest(
        name=processor_name,
        raw_document=document,
    )

    result = client.process_document(request=request)
    return result.document
