# services/firebase_service.py

import json
import firebase_admin
from firebase_admin import credentials, firestore, storage
import streamlit as st

# Prevent multiple initializations (Streamlit reruns)
if not firebase_admin._apps:
    cred_dict = json.loads(
        st.secrets["FIREBASE_SERVICE_ACCOUNT_JSON"]
    )

    cred = credentials.Certificate(cred_dict)

    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": f"{st.secrets['FIREBASE_PROJECT_ID']}.appspot.com"
        }
    )

# Firestore client
db = firestore.client()

# Storage bucket
bucket = storage.bucket()
