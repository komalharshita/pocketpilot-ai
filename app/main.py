# pocket_pilot.py
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from google import genai
import base64
from PIL import Image
import io
import json

# Page config
st.set_page_config(
    page_title="PocketPilot AI - Smart Expense Tracker",
    page_icon="💰",
    layout="wide"
)

# Gemini API setup
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    genai_client = None

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = [
        {"id": "1", "type": "Expense", "amount": 45.50, "category": "Food", "date": "2026-01-04", "merchant": "Campus Cafe", "notes": "Lunch with study group"},
        {"id": "2", "type": "Expense", "amount": 120.00, "category": "Transport", "date": "2026-01-03", "merchant": "Uber", "notes": "Weekly commute"},
        {"id": "3", "type": "Income", "amount": 500.00, "category": "Freelance", "date": "2026-01-02", "merchant": "Client Project", "notes": "Web design project"},
        {"id": "4", "type": "Expense", "amount": 89.99, "category": "Shopping", "date": "2026-01-01", "merchant": "Amazon", "notes": "Textbooks"},
        {"id": "5", "type": "Expense", "amount": 35.00, "category": "Entertainment", "date": "2025-12-30", "merchant": "Netflix", "notes": "Monthly subscription"},
        {"id": "6", "type": "Income", "amount": 1500.00, "category": "Salary", "date": "2025-12-28", "merchant": "Part-time Job", "notes": "December salary"},
    ]

if 'messages' not in st.session_state:
    st.session_state.messages = []

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

EXPENSE_CATEGORIES = ['Food', 'Transport', 'Groceries', 'Bills', 'Entertainment', 'Shopping', 'Health', 'Education', 'Other']
INCOME_CATEGORIES = ['Salary', 'Freelance', 'Investment', 'Other']

def get_summary():
    df = pd.DataFrame(st.session_state.transactions)
    if df.empty:
        return 0, 0, 0
    total_income = df[df['type'] == 'Income']['amount'].sum()
    total_expenses = df[df['type'] == 'Expense']['amount'].sum()
    return total_income, total_expenses, total_income - total_expenses

def get_transactions_context():
    """Get transaction summary for AI context"""
    df = pd.DataFrame(st.session_state.transactions)
    total_income, total_expenses, balance = get_summary()
    
    recent = df.head(10).to_dict('records')
    recent_str = "\n".join([f"- {t['date']}: {t['type']} ₹{t['amount']} ({t['category']}) - {t.get('merchant', 'N/A')}" for t in recent])
    
    return f"""
User's Financial Summary:
- Total Income: ₹{total_income:,.2f}
- Total Expenses: ₹{total_expenses:,.2f}
- Current Balance: ₹{balance:,.2f}

Recent Transactions:
{recent_str}
"""

def chat_with_pilot(user_message):
    """Chat with Gemini AI about finances"""
    if not GEMINI_API_KEY or not genai_client:
        return "⚠️ Please add your Gemini API key to .streamlit/secrets.toml"
    
    try:
        context = get_transactions_context()
        system_prompt = f"""You are Pilot, a friendly AI financial assistant for students. 
You help with budgeting, expense tracking, and financial advice.
Keep responses concise and actionable. Use ₹ for currency.

{context}
"""
        
        # Prepare conversation history
        history = [
            {"role": "user", "parts": [system_prompt]},
            {"role": "model", "parts": ["I understand! I'm Pilot, ready to help with your finances."]}
        ]
        
        # Add previous messages (last 10 for context)
        for msg in st.session_state.chat_history[-10:]:
            role = "user" if msg["role"] == "user" else "model"
            history.append({"role": role, "parts": [msg["content"]]})
        
        # Add current message
        history.append({"role": "user", "parts": [user_message]})
        
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=history
        )
        
        if response and hasattr(response, 'text'):
            return response.text.strip()
        return "I couldn't generate a response."
        
    except Exception as e:
        return f"❌ Error: {str(e)}"

def extract_receipt_with_gemini(image_bytes):
    """Use Gemini Vision to extract receipt data"""
    if not GEMINI_API_KEY or not genai_client:
        return None, "Please add your Gemini API key to .streamlit/secrets.toml"
    
    try:
        # Convert bytes to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        prompt = """Analyze this receipt image and extract the following information in JSON format:
{
    "merchant": "store/restaurant name",
    "amount": total amount as a number,
    "date": "YYYY-MM-DD format",
    "category": one of ["Food", "Transport", "Groceries", "Bills", "Entertainment", "Shopping", "Health", "Education", "Other"],
    "items": ["list of items if visible"]
}

If you cannot read certain fields, use null. Return ONLY the JSON, no other text."""

        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image]
        )
        
        # Parse JSON from response
        text = response.text.strip()
        # Remove markdown code blocks if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        data = json.loads(text)
        return data, None
    except Exception as e:
        return None, f"Error extracting receipt: {str(e)}"

# Sidebar navigation
st.sidebar.title("💰 PocketPilot AI")
st.sidebar.markdown("*Smart Finance for Students*")

if not GEMINI_API_KEY:
    st.sidebar.warning("⚠️ Add GEMINI_API_KEY to secrets")

page = st.sidebar.radio("Navigate", ["Dashboard", "Transactions", "Analytics", "Upload Receipt", "Chat with Pilot"])

# Dashboard
if page == "Dashboard":
    st.title("📊 Dashboard")
    
    total_income, total_expenses, balance = get_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Balance", f"₹{balance:,.2f}")
    with col2:
        st.metric("📈 Income", f"₹{total_income:,.2f}")
    with col3:
        st.metric("📉 Expenses", f"₹{total_expenses:,.2f}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Spending by Category")
        df = pd.DataFrame(st.session_state.transactions)
        expense_df = df[df['type'] == 'Expense']
        if not expense_df.empty:
            category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
            fig = px.pie(category_totals, values='amount', names='category', hole=0.4)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data available")
    
    with col2:
        st.subheader("📋 Recent Transactions")
        if st.session_state.transactions:
            for t in st.session_state.transactions[:5]:
                icon = "🔴" if t['type'] == 'Expense' else "🟢"
                sign = "-" if t['type'] == 'Expense' else "+"
                st.markdown(f"{icon} **{t.get('merchant', t['category'])}** - {sign}₹{t['amount']:,.2f}")
        else:
            st.info("No transactions yet")

# Transactions
elif page == "Transactions":
    st.title("💳 Transactions")
    
    with st.expander("➕ Add New Transaction", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            trans_type = st.selectbox("Type", ["Expense", "Income"])
            amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01)
            categories = EXPENSE_CATEGORIES if trans_type == "Expense" else INCOME_CATEGORIES
            category = st.selectbox("Category", categories)
        with col2:
            date = st.date_input("Date", datetime.now())
            merchant = st.text_input("Merchant")
            notes = st.text_area("Notes")
        
        if st.button("Add Transaction", type="primary"):
            new_trans = {
                "id": str(uuid.uuid4()),
                "type": trans_type,
                "amount": amount,
                "category": category,
                "date": str(date),
                "merchant": merchant,
                "notes": notes
            }
            st.session_state.transactions.insert(0, new_trans)
            st.success("Transaction added!")
            st.rerun()
    
    st.subheader("All Transactions")
    if st.session_state.transactions:
        for t in st.session_state.transactions:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                icon = "🔴" if t['type'] == 'Expense' else "🟢"
                st.markdown(f"{icon} **{t.get('merchant', t['category'])}** ({t['category']}) - {t['date']}")
            with col2:
                sign = "-" if t['type'] == 'Expense' else "+"
                st.markdown(f"**{sign}₹{t['amount']:,.2f}**")
            with col3:
                if st.button("🗑️", key=f"del_{t['id']}"):
                    st.session_state.transactions = [x for x in st.session_state.transactions if x['id'] != t['id']]
                    st.rerun()
    else:
        st.info("No transactions yet")

# Analytics
elif page == "Analytics":
    st.title("📈 Analytics")
    
    df = pd.DataFrame(st.session_state.transactions)
    
    if df.empty:
        st.info("No data available for analytics")
    else:
        df['date'] = pd.to_datetime(df['date'])
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Spending by Category")
            expense_df = df[df['type'] == 'Expense']
            if not expense_df.empty:
                category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
                fig = px.bar(category_totals, x='category', y='amount', color='category')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No expense data")
        
        with col2:
            st.subheader("Income vs Expenses")
            summary_df = df.groupby('type')['amount'].sum().reset_index()
            fig = px.bar(summary_df, x='type', y='amount', color='type')
            st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("🔥 Export Data")
        csv = df.to_csv(index=False)
        st.download_button("Download CSV", csv, "transactions.csv", "text/csv")

# Upload Receipt
elif page == "Upload Receipt":
    st.title("📸 Upload Receipt")
    st.markdown("Upload a receipt and **Gemini AI** will extract the details automatically.")
    
    uploaded_file = st.file_uploader("Choose a receipt image", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Receipt", width=300)
        
        with col2:
            if st.button("🤖 Extract with Gemini AI", type="primary"):
                with st.spinner("Analyzing receipt with Gemini Vision..."):
                    image_bytes = uploaded_file.getvalue()
                    data, error = extract_receipt_with_gemini(image_bytes)
                    
                    if error:
                        st.error(error)
                    elif data:
                        st.success("✅ Receipt analyzed!")
                        st.json(data)
                        
                        # Auto-add transaction
                        if st.button("➕ Add as Transaction"):
                            new_trans = {
                                "id": str(uuid.uuid4()),
                                "type": "Expense",
                                "amount": float(data.get('amount', 0)),
                                "category": data.get('category', 'Other'),
                                "date": data.get('date', str(datetime.now().date())),
                                "merchant": data.get('merchant', 'Unknown'),
                                "notes": f"Items: {', '.join(data.get('items', []))}" if data.get('items') else ""
                            }
                            st.session_state.transactions.insert(0, new_trans)
                            st.success("Transaction added!")
                            st.rerun()

# Chat with Pilot
elif page == "Chat with Pilot":
    st.title("🤖 Chat with Pilot")
    st.caption("Your personal finance assistant")

    # Financial Summary
    total_income, total_expenses, balance = get_summary()

    st.markdown(
        f"""
        <div style="
            background:#f2f2f2;
            padding:20px;
            border-radius:16px;
            margin-bottom:16px;
        ">
        👋 <b>Hi! I'm Pilot</b>, your AI finance assistant.  
        I can help you understand your spending and improve budgeting.

        <br><br>
        <b>Here's a quick overview:</b><br>
        • Total Balance: ₹{balance:,.2f}<br>
        • Total Income: ₹{total_income:,.2f}<br>
        • Total Expenses: ₹{total_expenses:,.2f}

        <br><br>
        Ask me anything about your finances!
        </div>
        """,
        unsafe_allow_html=True
    )

    # Suggestion Chips
    st.markdown("**Try asking:**")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("✨ How much did I spend on food this month?"):
            st.session_state.quick_query = "How much did I spend on food this month?"
        if st.button("✨ Give me 3 tips to save money"):
            st.session_state.quick_query = "Give me 3 simple tips to save money"

    with col2:
        if st.button("✨ What's my biggest expense category?"):
            st.session_state.quick_query = "What's my biggest expense category?"
        if st.button("✨ Summarize my spending this week"):
            st.session_state.quick_query = "Summarize my spending this week"

    # Chat History
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='text-align:right; background:#e0e7ff; padding:12px; border-radius:12px; margin:8px 0;'>"
                f"<b>You:</b><br>{msg['content']}</div>",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"<div style='background:#f9fafb; padding:12px; border-radius:12px; margin:8px 0;'>"
                f"<b>🤖 Pilot:</b><br>{msg['content']}</div>",
                unsafe_allow_html=True
            )

    # Chat Input
    user_input = st.text_input(
        "Ask Pilot about your finances...",
        value=st.session_state.get("quick_query", ""),
        key="chat_input"
    )

    if "quick_query" in st.session_state:
        del st.session_state.quick_query

    if st.button("🚀 Send"):
        if user_input.strip():
            st.session_state.chat_history.append({
                "role": "user",
                "content": user_input
            })

            with st.spinner("Pilot is thinking..."):
                response = chat_with_pilot(user_input)

            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response
            })

            st.rerun()