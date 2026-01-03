# services/firebase_auth.py

import os
import requests
import streamlit as st

# Read API key from environment or Streamlit secrets
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY") or st.secrets.get("FIREBASE_API_KEY")

if not FIREBASE_API_KEY:
    raise ValueError("FIREBASE_API_KEY not set in environment or Streamlit secrets")

# Firebase REST endpoints
_SIGNIN_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
_SIGNUP_URL = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"

class FirebaseAuthClient:
    def __init__(self):
        # mimic pyrebase auth object
        self._signin_url = _SIGNIN_URL
        self._signup_url = _SIGNUP_URL

    def sign_in_with_email_and_password(self, email: str, password: str):
        """
        Sign in a user. Returns the JSON response similar to pyrebase:
        { 'idToken': <idToken>, 'localId': <uid>, ... }
        Raises requests.HTTPError for bad credentials.
        """
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        resp = requests.post(self._signin_url, json=payload, timeout=15)
        if resp.status_code != 200:
            # raise a clear error for the UI to catch
            resp.raise_for_status()
        return resp.json()

    def create_user_with_email_and_password(self, email: str, password: str):
        """
        Create a new user. Returns JSON response from Firebase.
        Raises requests.HTTPError if creation fails.
        """
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        resp = requests.post(self._signup_url, json=payload, timeout=15)
        if resp.status_code != 200:
            resp.raise_for_status()
        return resp.json()

# export an 'auth' object so existing code can do: from services.firebase_auth import auth
auth = FirebaseAuthClient()
