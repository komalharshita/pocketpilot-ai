# app/main.py

import streamlit as st
from app.auth import login_signup

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
    st.subheader("Dashboard")
    st.info("Financial overview will appear here.")

elif page == "Add Transaction":
    st.subheader("Add Transaction")
    st.info("Expense and income entry form will be added here.")

elif page == "Upload Receipt":
    st.subheader("Upload Receipt")
    st.info("Receipt upload and extraction will be handled here.")

elif page == "Chat with Pilot":
    st.subheader("Chat with Pilot")
    st.info("Ask questions about your spending here.")
