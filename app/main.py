import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import sys

# ------------------ PATH SETUP ------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# ------------------ IMPORT SERVICES ------------------
try:
    from services.gemini_service import GeminiClient
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    print("Gemini service unavailable:", e)

try:
    from services.document_service import DocumentAIClient, MockDocumentAIClient
    DOCUMENT_AI_AVAILABLE = True
except Exception:
    DOCUMENT_AI_AVAILABLE = False

# ------------------ ENV & PAGE CONFIG ------------------
load_dotenv()

st.set_page_config(
    page_title="PocketPilot AI",
    page_icon="💰",
    layout="wide"
)

# ------------------ SESSION STATE ------------------
if "transactions" not in st.session_state:
    st.session_state.transactions = pd.DataFrame([
        {
            "id": 1,
            "type": "Expense",
            "amount": 250,
            "category": "Food",
            "date": datetime.now() - timedelta(days=2),
            "merchant": "Restaurant",
            "notes": ""
        },
        {
            "id": 2,
            "type": "Income",
            "amount": 5000,
            "category": "Allowance",
            "date": datetime.now() - timedelta(days=5),
            "merchant": "Parent",
            "notes": ""
        }
    ])

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "gemini_client" not in st.session_state:
    api_key = os.getenv("GOOGLE_API_KEY")
    if GEMINI_AVAILABLE and api_key:
        try:
            st.session_state.gemini_client = GeminiClient(api_key)
        except Exception:
            st.session_state.gemini_client = None
    else:
        st.session_state.gemini_client = None

# ------------------ HELPERS ------------------
def financial_summary():
    df = st.session_state.transactions
    income = df[df["type"] == "Income"]["amount"].sum()
    expense = df[df["type"] == "Expense"]["amount"].sum()
    return income, expense, income - expense

# ------------------ SIDEBAR ------------------
st.sidebar.title("💰 PocketPilot AI")
page = st.sidebar.radio(
    "Navigate",
    [
        "📊 Dashboard",
        "➕ Add Transaction",
        "📋 Transactions",
        "🤖 AI Pilot Chat"
    ]
)

# ------------------ DASHBOARD ------------------
if page == "📊 Dashboard":
    income, expense, balance = financial_summary()

    c1, c2, c3 = st.columns(3)
    c1.metric("Income", f"₹{income:,.0f}")
    c2.metric("Expenses", f"₹{expense:,.0f}")
    c3.metric("Balance", f"₹{balance:,.0f}")

    st.subheader("Spending by Category")
    df = st.session_state.transactions
    expense_df = df[df["type"] == "Expense"]
    if not expense_df.empty:
        fig = px.pie(
            expense_df,
            values="amount",
            names="category",
            hole=0.4
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No expenses yet")

# ------------------ ADD TRANSACTION ------------------
elif page == "➕ Add Transaction":
    st.header("Add Transaction")

    with st.form("add_tx"):
        t_type = st.selectbox("Type", ["Expense", "Income"])
        amt = st.number_input("Amount", min_value=1.0)
        cat = st.text_input("Category")
        merchant = st.text_input("Merchant")
        submitted = st.form_submit_button("Add")

    if submitted:
        new_id = len(st.session_state.transactions) + 1
        st.session_state.transactions.loc[len(st.session_state.transactions)] = [
            new_id, t_type, amt, cat, datetime.now(), merchant, ""
        ]
        st.success("Transaction added")

# ------------------ TRANSACTIONS ------------------
elif page == "📋 Transactions":
    st.header("All Transactions")
    st.dataframe(st.session_state.transactions, use_container_width=True)

# ------------------ AI CHAT (SIMPLIFIED & SAFE) ------------------
elif page == "🤖 AI Pilot Chat":
    st.header("🤖 AI Pilot (Simple Mode)")

    if not st.session_state.gemini_client:
        st.warning("Gemini API not configured. Showing demo responses.")

    # ---- QUICK PROMPTS ----
    st.subheader("Quick Prompts")
    col1, col2, col3 = st.columns(3)

    quick_prompts = {
        "📊 Spending Summary": "Give me a simple summary of my spending habits.",
        "💡 Budget Tips": "Give me 5 simple budgeting tips for students.",
        "💰 Saving Advice": "How can a student save more money every month?"
    }

    for col, (label, prompt) in zip([col1, col2, col3], quick_prompts.items()):
        with col:
            if st.button(label):
                st.session_state.chat_history.append(
                    {"role": "user", "content": prompt}
                )

                if st.session_state.gemini_client:
                    try:
                        reply = st.session_state.gemini_client.ask(prompt)
                    except Exception:
                        reply = "⚠️ Gemini is temporarily unavailable. Please try again later."
                else:
                    reply = "💡 Demo Mode: Track expenses, set limits, and save at least 20% monthly."

                st.session_state.chat_history.append(
                    {"role": "assistant", "content": reply}
                )
                st.rerun()

    # ---- CHAT HISTORY ----
    st.markdown("---")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(f"**You:** {msg['content']}")
        else:
            st.markdown(f"**🤖 Pilot:** {msg['content']}")

    # ---- MANUAL INPUT ----
    user_input = st.text_input("Ask something else:")
    if st.button("Send") and user_input:
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input}
        )

        if st.session_state.gemini_client:
            try:
                reply = st.session_state.gemini_client.ask(user_input)
            except Exception:
                reply = "⚠️ Gemini error. Please retry."
        else:
            reply = "💡 Demo response: Build a habit of reviewing expenses weekly."

        st.session_state.chat_history.append(
            {"role": "assistant", "content": reply}
        )
        st.rerun()

# ------------------ FOOTER ------------------
st.sidebar.markdown("---")
st.sidebar.markdown("Built with ❤️ for Hackathons")
st.sidebar.markdown("PocketPilot AI · v1 (Stable)")
