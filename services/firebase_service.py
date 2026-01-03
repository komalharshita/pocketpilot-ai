# services/firebase_service.py

import os
import firebase_admin
from firebase_admin import credentials, firestore, storage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Singleton pattern to prevent multiple initializations
if not firebase_admin._apps:
    cred_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

    if not cred_path:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set")

    cred = credentials.Certificate(cred_path)

    firebase_admin.initialize_app(
        cred,
        {
            "storageBucket": f"{os.getenv('FIREBASE_PROJECT_ID')}.appspot.com"
        }
    )

# Firestore client
db = firestore.client()

# Storage bucket
bucket = storage.bucket()
