# services/document_ai_service.py

import os
from google.cloud import documentai_v1 as documentai
from dotenv import load_dotenv

load_dotenv()

PROJECT_ID = os.getenv("DOCUMENT_AI_PROJECT_ID")
LOCATION = os.getenv("DOCUMENT_AI_LOCATION")
PROCESSOR_ID = os.getenv("DOCUMENT_AI_PROCESSOR_ID")

if not all([PROJECT_ID, LOCATION, PROCESSOR_ID]):
    raise ValueError("Document AI environment variables not set")

def parse_receipt(file_bytes: bytes, mime_type: str):
    """
    Sends a receipt file to Document AI and returns extracted entities.
    """
    client = documentai.DocumentProcessorServiceClient()

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
