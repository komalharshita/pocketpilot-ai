# services/firebase.py

import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore


def init_firebase():
    """
    Initialize Firebase using service account stored in Streamlit secrets.
    Runs only once.
    """
    if firebase_admin._apps:
        return firestore.client()

    service_account_json = st.secrets.get("FIREBASE_SERVICE_ACCOUNT_JSON")

    if not service_account_json:
        raise RuntimeError("Firebase service account JSON not found in secrets")

    cred_dict = json.loads(service_account_json)
    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(cred)
    return firestore.client()


# Firestore DB (import this wherever needed)
db = init_firebase()
