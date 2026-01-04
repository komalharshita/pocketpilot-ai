# app/auth.py

import streamlit as st
import pyrebase

# Firebase config from secrets
firebase_config = {
    "apiKey": st.secrets["FIREBASE_API_KEY"],
    "authDomain": st.secrets["FIREBASE_AUTH_DOMAIN"],
    "projectId": st.secrets["FIREBASE_PROJECT_ID"],
}

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


def login_signup():
    st.subheader("Login / Sign Up")

    mode = st.radio("Choose action", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if mode == "Login":
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state.user = {
                    "email": email,
                    "uid": user["localId"]
                }
                st.success("Logged in successfully")
                st.rerun()
            except Exception:
                st.error("Invalid email or password")

    else:
        if st.button("Sign Up"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created. Please log in.")
            except Exception:
                st.error("Account creation failed")
