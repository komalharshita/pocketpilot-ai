from google.cloud import documentai_v1 as documentai
from pathlib import Path


def extract_text_from_receipt(
    file_path: str,
    project_id: str,
    location: str,
    processor_id: str
):
    """
    Sends receipt to Google Document AI and returns extracted text.
    """

    client = documentai.DocumentProcessorServiceClient()

    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    file_path = Path(file_path)
    mime_type = "application/pdf" if file_path.suffix == ".pdf" else "image/jpeg"

    with open(file_path, "rb") as f:
        file_content = f.read()

    raw_document = documentai.RawDocument(
        content=file_content,
        mime_type=mime_type
    )

    request = documentai.ProcessRequest(
        name=name,
        raw_document=raw_document
    )

    result = client.process_document(request=request)

    document = result.document

    return document.text
