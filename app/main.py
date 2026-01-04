# app/main.py

import streamlit as st
from auth import login_signup
from upload_receipt import upload_receipt_page
from expenses import expenses_page
from chat import chat_page

st.set_page_config(
    page_title="PocketPilot Lite",
    page_icon="💳",
    layout="centered"
)

st.title("PocketPilot Lite")

# Initialize session
if "user" not in st.session_state:
    st.session_state.user = None

# If user not logged in → show auth page
if st.session_state.user is None:
    login_signup()
    st.stop()

# Sidebar navigation
with st.sidebar:
    st.success(f"Logged in as {st.session_state.user['email']}")
    page = st.radio(
        "Navigate",
        ["Upload Receipt", "My Expenses", "Chatbot"]
    )

    if st.button("Logout"):
        st.session_state.user = None
        st.rerun()

# Page routing
if page == "Upload Receipt":
    upload_receipt_page(st.session_state.user)

elif page == "My Expenses":
    expenses_page(st.session_state.user)

elif page == "Chatbot":
    chat_page(st.session_state.user)
