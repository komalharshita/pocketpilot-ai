from services.document_ai_service import parse_receipt

if __name__ == "__main__":
    with open("tests/sample_receipt.jpg", "rb") as f:
        file_bytes = f.read()

    doc = parse_receipt(file_bytes, "image/jpeg")

    print("Extracted Entities:")
    for entity in doc.entities:
        print(entity.type_, ":", entity.mention_text)
