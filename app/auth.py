# app/auth.py

import streamlit as st
import requests

FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]

SIGN_UP_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signUp"
    f"?key={FIREBASE_API_KEY}"
)

SIGN_IN_URL = (
    "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
    f"?key={FIREBASE_API_KEY}"
)


def login_signup():
    st.subheader("Login / Sign Up")

    mode = st.radio("Choose action", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if not email or not password:
        return

    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    if mode == "Login":
        if st.button("Login"):
            response = requests.post(SIGN_IN_URL, json=payload)
            data = response.json()

            if "localId" in data:
                st.session_state.user = {
                    "email": email,
                    "uid": data["localId"]
                }
                st.success("Logged in successfully")
                st.rerun()
            else:
                st.error(data.get("error", {}).get("message", "Login failed"))

    else:
        if st.button("Sign Up"):
            response = requests.post(SIGN_UP_URL, json=payload)
            data = response.json()

            if "localId" in data:
                st.success("Account created. Please log in.")
            else:
                st.error(data.get("error", {}).get("message", "Signup failed"))
