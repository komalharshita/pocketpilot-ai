# app/auth.py

import streamlit as st
from services.firebase_auth import auth

def login_signup():
    st.subheader("Login / Sign Up")

    mode = st.radio("Choose action", ["Login", "Sign Up"])

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if mode == "Login":
        if st.button("Login"):
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                st.session_state["user"] = user

                # Do NOT show success message before rerun
                st.experimental_rerun()

            except Exception:
                st.error("Invalid email or password")

    else:
        if st.button("Sign Up"):
            try:
                auth.create_user_with_email_and_password(email, password)
                st.success("Account created successfully. Please log in.")
            except Exception:
                st.error("Account creation failed")
