# app/main.py

import streamlit as st
from app.auth import login_signup
from app.add_transaction import add_transaction_page
from app.transaction_list import transaction_list
from app.dashboard import dashboard_page
from app.chat import chat_page
from app.upload_receipt import upload_receipt_page

if "user" not in st.session_state:
    login_signup()
    st.stop()

# --------------------------------------------------
# App Configuration
# --------------------------------------------------
st.set_page_config(
    page_title="PocketPilot AI",
    page_icon="💼",
    layout="wide"
)

# --------------------------------------------------
# App Title
# --------------------------------------------------
st.title("PocketPilot AI")
st.caption("AI-powered expense tracking with Gemini and Google Cloud")

# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------
st.sidebar.header("Navigation")

page = st.sidebar.radio(
    "Go to",
    [
        "Dashboard",
        "Add Transaction",
        "Upload Receipt",
        "Chat with Pilot"
    ]
)

st.sidebar.divider()
if st.sidebar.button("Logout"):
    st.session_state.clear()
    st.experimental_rerun()


# --------------------------------------------------
# Page Routing (Skeleton Only)
# --------------------------------------------------

if page == "Dashboard":
    dashboard_page(st.session_state["user"])

elif page == "Add Transaction":
    add_transaction_page(st.session_state["user"])

elif page == "Upload Receipt":
    st.subheader("Upload Receipt")
    st.info("Receipt upload and extraction will be handled here.")

elif page == "Chat with Pilot":
    chat_page(st.session_state["user"])
