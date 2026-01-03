# services/firebase_auth.py

import os
import pyrebase
from dotenv import load_dotenv

load_dotenv()

import streamlit as st

firebase_config = {
    "apiKey": os.getenv("FIREBASE_API_KEY") or st.secrets["FIREBASE_API_KEY"],
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN") or st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": os.getenv("FIREBASE_PROJECT_ID") or st.secrets["FIREBASE_PROJECT_ID"],
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET") or st.secrets["FIREBASE_STORAGE_BUCKET"],
    "appId": os.getenv("FIREBASE_APP_ID") or st.secrets["FIREBASE_APP_ID"],
}


firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()
