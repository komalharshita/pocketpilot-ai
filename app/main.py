# --- PYTHONPATH FIX (REQUIRED FOR STREAMLIT CLOUD) ---
import sys
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
# ---------------------------------------------------


import streamlit as st
from auth import login_signup
from add_transaction import add_transaction_page
from transaction_list import transaction_list
from dashboard import dashboard_page
from chat import chat_page
from upload_receipt import upload_receipt_page

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
    upload_receipt_page(st.session_state["user"])

elif page == "Chat with Pilot":
    chat_page(st.session_state["user"])
