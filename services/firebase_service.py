# services/firebase_service.py

import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st

def load_service_account():
    raw = st.secrets.get("FIREBASE_SERVICE_ACCOUNT_JSON")

    if not raw:
        raise RuntimeError("FIREBASE_SERVICE_ACCOUNT_JSON is missing from secrets")

    # Normalize line endings
    raw = raw.replace("\r", "")

    # Attempt parse directly
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass  # try sanitization below

    # Sanitize private_key newlines
    if '"private_key"' in raw:
        start = raw.find('"private_key"')
        colon = raw.find(":", start)
        first_quote = raw.find('"', colon + 1)
        second_quote = raw.find('"', first_quote + 1)

        key_body = raw[first_quote + 1 : second_quote]
        key_body = key_body.replace("\n", "\\n")

        raw = raw[: first_quote + 1] + key_body + raw[second_quote:]

    # Final attempt
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise RuntimeError(
            "FIREBASE_SERVICE_ACCOUNT_JSON is still invalid JSON.\n"
            "Re-download the service account JSON and paste it unmodified "
            "inside triple quotes."
        ) from e


# Initialize Firebase Admin (safe for Streamlit reruns)
if not firebase_admin._apps:
    cred_dict = load_service_account()

    if cred_dict.get("type") != "service_account":
        raise ValueError("Invalid Firebase service account JSON")

    cred = credentials.Certificate(cred_dict)

    bucket_name = (
        st.secrets.get("FIREBASE_STORAGE_BUCKET")
        or f"{cred_dict['project_id']}.appspot.com"
    )

    firebase_admin.initialize_app(
        cred,
        {"storageBucket": bucket_name},
    )

db = firestore.client()
bucket = storage.bucket()
