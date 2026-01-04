# pocket_pilot.py - COMPLETE FIXED VERSION
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import uuid
from google import genai
from PIL import Image
import io
import json

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="PocketPilot AI - Smart Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM CSS FOR BETTER UI/UX
# ============================================================================
st.markdown("""
<style>
    /* Main theme colors - Accessible & Clean */
    :root {
        --primary-blue: #4F46E5;
        --primary-blue-dark: #4338CA;
        --secondary-green: #10B981;
        --danger-red: #EF4444;
        --bg-light: #F9FAFB;
        --bg-white: #FFFFFF;
        --text-dark: #1F2937;
        --text-medium: #6B7280;
        --border-color: #E5E7EB;
    }
    
    /* Chat container styling */
    .chat-container {
        background: var(--bg-white);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* User message bubble */
    .user-message {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: white;
        padding: 16px 20px;
        border-radius: 18px 18px 4px 18px;
        margin: 12px 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
        animation: slideInRight 0.3s ease-out;
    }
    
    /* Assistant message bubble */
    .assistant-message {
        background: var(--bg-light);
        color: var(--text-dark);
        padding: 16px 20px;
        border-radius: 18px 18px 18px 4px;
        margin: 12px 0;
        margin-right: 20%;
        border-left: 4px solid var(--primary-blue);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        animation: slideInLeft 0.3s ease-out;
    }
    
    /* Message labels */
    .message-label {
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 8px;
        opacity: 0.9;
    }
    
    /* Animations */
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Suggestion chips */
    .stButton button {
        border-radius: 20px;
        border: 2px solid var(--border-color);
        background: white;
        color: var(--text-dark);
        padding: 8px 16px;
        font-size: 0.9rem;
        transition: all 0.2s;
        width: 100%;
        text-align: left;
    }
    
    .stButton button:hover {
        border-color: var(--primary-blue);
        background: var(--primary-blue);
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3);
    }
    
    /* Input field styling */
    .stTextInput input {
        border-radius: 12px;
        border: 2px solid var(--border-color);
        padding: 12px 16px;
        font-size: 1rem;
        transition: border-color 0.2s;
    }
    
    .stTextInput input:focus {
        border-color: var(--primary-blue);
        box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.1);
    }
    
    /* Info box */
    .info-box {
        background: linear-gradient(135deg, #667EEA 0%, #764BA2 100%);
        color: white;
        padding: 24px;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    
    /* Metrics */
    .metric-card {
        background: white;
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid var(--primary-blue);
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Improve sidebar */
    .css-1d391kg {
        background-color: #F9FAFB;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# GEMINI API SETUP
# ============================================================================
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
genai_client = None

if GEMINI_API_KEY:
    try:
        genai_client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize Gemini: {str(e)}")

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'transactions' not in st.session_state:
    st.session_state.transactions = [
        {"id": "1", "type": "Expense", "amount": 45.50, "category": "Food", "date": "2026-01-04", "merchant": "Campus Cafe", "notes": "Lunch with study group"},
        {"id": "2", "type": "Expense", "amount": 120.00, "category": "Transport", "date": "2026-01-03", "merchant": "Uber", "notes": "Weekly commute"},
        {"id": "3", "type": "Income", "amount": 500.00, "category": "Freelance", "date": "2026-01-02", "merchant": "Client Project", "notes": "Web design project"},
        {"id": "4", "type": "Expense", "amount": 89.99, "category": "Shopping", "date": "2026-01-01", "merchant": "Amazon", "notes": "Textbooks"},
        {"id": "5", "type": "Expense", "amount": 35.00, "category": "Entertainment", "date": "2025-12-30", "merchant": "Netflix", "notes": "Monthly subscription"},
        {"id": "6", "type": "Income", "amount": 1500.00, "category": "Salary", "date": "2025-12-28", "merchant": "Part-time Job", "notes": "December salary"},
    ]

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'user_input' not in st.session_state:
    st.session_state.user_input = ""

if 'processing' not in st.session_state:
    st.session_state.processing = False

# ============================================================================
# CONSTANTS
# ============================================================================
EXPENSE_CATEGORIES = ['Food', 'Transport', 'Groceries', 'Bills', 'Entertainment', 'Shopping', 'Health', 'Education', 'Other']
INCOME_CATEGORIES = ['Salary', 'Freelance', 'Investment', 'Other']

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_summary():
    """Calculate financial summary"""
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
    
    # Get category breakdown
    expense_df = df[df['type'] == 'Expense']
    if not expense_df.empty:
        top_categories = expense_df.groupby('category')['amount'].sum().sort_values(ascending=False).head(5)
        category_str = "\n".join([f"  • {cat}: ₹{amt:,.2f}" for cat, amt in top_categories.items()])
    else:
        category_str = "  No expense data"
    
    # Get recent transactions
    recent = df.head(10).to_dict('records')
    recent_str = "\n".join([f"  • {t['date']}: {t['type']} ₹{t['amount']:,.2f} - {t['category']} ({t.get('merchant', 'N/A')})" for t in recent])
    
    return f"""User's Financial Summary:
━━━━━━━━━━━━━━━━━━━━━━━━━━━
💰 Total Balance: ₹{balance:,.2f}
📈 Total Income: ₹{total_income:,.2f}
📉 Total Expenses: ₹{total_expenses:,.2f}
💵 Savings Rate: {(balance/total_income*100) if total_income > 0 else 0:.1f}%

Top Spending Categories:
{category_str}

Recent Transactions (Last 10):
{recent_str}
━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

def chat_with_pilot(user_message: str) -> str:
    """
    Send message to Gemini AI and get response
    FIX: Correct API format for google-genai SDK
    """
    if not GEMINI_API_KEY or not genai_client:
        return "⚠️ **API Key Missing**: Please add your Gemini API key to `.streamlit/secrets.toml`\n\nExample:\n```\nGEMINI_API_KEY = \"your-api-key-here\"\n```"
    
    if not user_message or not user_message.strip():
        return "Please ask a valid question about your finances."
    
    try:
        # Build context with system prompt
        context = get_transactions_context()
        
        system_prompt = f"""You are Pilot, a friendly AI financial assistant for students.

Your role:
• Help users understand their spending patterns
• Provide actionable budgeting advice
• Answer questions about their transactions
• Give simple, practical financial tips

Guidelines:
• Be concise and actionable (2-4 sentences usually)
• Use emojis sparingly for clarity (💡, 💰, 📊)
• Use ₹ symbol for Indian Rupees
• Be encouraging and supportive

Current User Data:
{context}

Remember: Keep responses SHORT and HELPFUL."""

        # FIX: Build conversation string instead of complex dict structure
        # The google-genai SDK expects simpler format
        conversation = system_prompt + "\n\n"
        
        # Add conversation history
        for msg in st.session_state.chat_history[-6:]:  # Last 6 messages
            role_label = "User" if msg["role"] == "user" else "Pilot"
            conversation += f"{role_label}: {msg['content']}\n\n"
        
        # Add current message
        conversation += f"User: {user_message}\n\nPilot:"
        
        # Call Gemini API with simple string prompt
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=conversation
        )
        
        # Extract response text
        if response and hasattr(response, 'text') and response.text:
            return response.text.strip()
        else:
            return "I couldn't generate a response. Please try rephrasing your question."
            
    except Exception as e:
        error_msg = str(e)
        if "API_KEY" in error_msg.upper():
            return "⚠️ **API Key Error**: Your Gemini API key may be invalid or expired. Please check your configuration."
        elif "QUOTA" in error_msg.upper():
            return "⚠️ **Quota Exceeded**: You've reached your API usage limit. Please try again later."
        elif "RATE_LIMIT" in error_msg.upper():
            return "⚠️ **Rate Limited**: Too many requests. Please wait a moment and try again."
        else:
            return f"❌ **Error**: {error_msg}\n\nPlease try again or rephrase your question."

def extract_receipt_with_gemini(image_bytes):
    """Use Gemini Vision to extract receipt data"""
    if not GEMINI_API_KEY or not genai_client:
        return None, "Please add your Gemini API key to .streamlit/secrets.toml"
    
    try:
        image = Image.open(io.BytesIO(image_bytes))
        
        prompt = """Analyze this receipt image and extract information in this EXACT JSON format:
{
    "merchant": "store/restaurant name",
    "amount": 0.00,
    "date": "YYYY-MM-DD",
    "category": "Food",
    "items": ["item1", "item2"]
}

Rules:
- category must be one of: Food, Transport, Groceries, Bills, Entertainment, Shopping, Health, Education, Other
- amount must be a number (no currency symbols)
- date must be YYYY-MM-DD format
- Use null for fields you cannot read
- Return ONLY valid JSON, no markdown, no explanations"""

        # FIX: Correct format for vision API with image
        response = genai_client.models.generate_content(
            model="gemini-1.5-flash",
            contents=[prompt, image]  # Simple list format works for mixed content
        )
        
        text = response.text.strip()
        # Clean markdown formatting
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        
        data = json.loads(text.strip())
        
        # Validate required fields
        if not data.get("amount") or not data.get("category"):
            return None, "Could not extract required fields from receipt"
            
        return data, None
        
    except json.JSONDecodeError:
        return None, "Failed to parse receipt data. Please try a clearer image."
    except Exception as e:
        return None, f"Error processing receipt: {str(e)}"

# ============================================================================
# CHAT INPUT HANDLER - FIX: Proper state management
# ============================================================================

def handle_chat_submit():
    """
    Handle chat message submission
    FIX: This function is called when user submits message
    """
    user_message = st.session_state.chat_input_field
    
    if not user_message or not user_message.strip():
        return
    
    # Add user message to history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_message
    })
    
    # Set processing flag
    st.session_state.processing = True
    
    # Get AI response
    with st.spinner("🤔 Pilot is thinking..."):
        response = chat_with_pilot(user_message)
    
    # Add assistant response to history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })
    
    # Clear processing flag
    st.session_state.processing = False
    
    # Clear input field
    st.session_state.chat_input_field = ""

def handle_quick_query(query: str):
    """Handle quick query button clicks"""
    st.session_state.chat_input_field = query
    handle_chat_submit()

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
st.sidebar.title("💰 PocketPilot AI")
st.sidebar.markdown("*Smart Finance for Students*")

if not GEMINI_API_KEY:
    st.sidebar.error("⚠️ Add GEMINI_API_KEY to secrets")
else:
    st.sidebar.success("✅ API Connected")

page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Transactions", "Analytics", "Upload Receipt", "Chat with Pilot"],
    label_visibility="collapsed"
)

# ============================================================================
# DASHBOARD PAGE
# ============================================================================
if page == "Dashboard":
    st.title("📊 Financial Dashboard")
    
    total_income, total_expenses, balance = get_summary()
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💰 Balance", f"₹{balance:,.2f}", 
                 delta=f"{(balance/total_income*100) if total_income > 0 else 0:.1f}% savings")
    with col2:
        st.metric("📈 Income", f"₹{total_income:,.2f}")
    with col3:
        st.metric("📉 Expenses", f"₹{total_expenses:,.2f}")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💸 Spending by Category")
        df = pd.DataFrame(st.session_state.transactions)
        expense_df = df[df['type'] == 'Expense']
        if not expense_df.empty:
            category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
            fig = px.pie(category_totals, values='amount', names='category', hole=0.4,
                        color_discrete_sequence=px.colors.qualitative.Set3)
            fig.update_traces(textposition='inside', textinfo='percent+label')
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
                st.caption(f"{t['date']} • {t['category']}")
        else:
            st.info("No transactions yet")

# ============================================================================
# TRANSACTIONS PAGE
# ============================================================================
elif page == "Transactions":
    st.title("💳 Manage Transactions")
    
    with st.expander("➕ Add New Transaction", expanded=True):
        with st.form("add_transaction_form"):
            col1, col2 = st.columns(2)
            with col1:
                trans_type = st.selectbox("Type", ["Expense", "Income"])
                amount = st.number_input("Amount (₹)", min_value=0.01, step=0.01, format="%.2f")
                categories = EXPENSE_CATEGORIES if trans_type == "Expense" else INCOME_CATEGORIES
                category = st.selectbox("Category", categories)
            with col2:
                date = st.date_input("Date", datetime.now())
                merchant = st.text_input("Merchant/Source")
                notes = st.text_area("Notes (optional)")
            
            submitted = st.form_submit_button("Add Transaction", type="primary", use_container_width=True)
            
            if submitted:
                new_trans = {
                    "id": str(uuid.uuid4()),
                    "type": trans_type,
                    "amount": float(amount),
                    "category": category,
                    "date": str(date),
                    "merchant": merchant if merchant else category,
                    "notes": notes
                }
                st.session_state.transactions.insert(0, new_trans)
                st.success(f"✅ Transaction added: {trans_type} of ₹{amount:,.2f}")
                st.rerun()
    
    st.subheader("All Transactions")
    
    if st.session_state.transactions:
        for t in st.session_state.transactions:
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 0.5])
                with col1:
                    icon = "🔴" if t['type'] == 'Expense' else "🟢"
                    st.markdown(f"{icon} **{t.get('merchant', t['category'])}**")
                    st.caption(f"{t['date']} • {t['category']}")
                with col2:
                    sign = "-" if t['type'] == 'Expense' else "+"
                    st.markdown(f"### {sign}₹{t['amount']:,.2f}")
                with col3:
                    if st.button("🗑️", key=f"del_{t['id']}"):
                        st.session_state.transactions = [x for x in st.session_state.transactions if x['id'] != t['id']]
                        st.rerun()
                st.divider()
    else:
        st.info("No transactions yet. Add your first transaction above!")

# ============================================================================
# ANALYTICS PAGE
# ============================================================================
elif page == "Analytics":
    st.title("📈 Financial Analytics")
    
    df = pd.DataFrame(st.session_state.transactions)
    
    if df.empty:
        st.info("No data available for analytics. Add some transactions first!")
    else:
        df['date'] = pd.to_datetime(df['date'])
        
        # Summary stats
        col1, col2, col3, col4 = st.columns(4)
        
        total_income, total_expenses, balance = get_summary()
        avg_expense = df[df['type'] == 'Expense']['amount'].mean()
        
        with col1:
            st.metric("Total Income", f"₹{total_income:,.2f}")
        with col2:
            st.metric("Total Expenses", f"₹{total_expenses:,.2f}")
        with col3:
            st.metric("Net Balance", f"₹{balance:,.2f}")
        with col4:
            st.metric("Avg. Expense", f"₹{avg_expense:,.2f}")
        
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Spending by Category")
            expense_df = df[df['type'] == 'Expense']
            if not expense_df.empty:
                category_totals = expense_df.groupby('category')['amount'].sum().reset_index()
                category_totals = category_totals.sort_values('amount', ascending=False)
                fig = px.bar(category_totals, x='amount', y='category', orientation='h',
                           color='amount', color_continuous_scale='Viridis')
                fig.update_layout(showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("💰 Income vs Expenses")
            summary_df = df.groupby('type')['amount'].sum().reset_index()
            fig = px.bar(summary_df, x='type', y='amount', color='type',
                       color_discrete_map={'Income': '#10B981', 'Expense': '#EF4444'})
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Time series
        st.subheader("📅 Spending Over Time")
        daily_expenses = df[df['type'] == 'Expense'].groupby('date')['amount'].sum().reset_index()
        if not daily_expenses.empty:
            fig = px.line(daily_expenses, x='date', y='amount', markers=True)
            fig.update_traces(line_color='#EF4444')
            st.plotly_chart(fig, use_container_width=True)
        
        st.divider()
        
        # Export
        st.subheader("🔥 Export Data")
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ============================================================================
# UPLOAD RECEIPT PAGE
# ============================================================================
elif page == "Upload Receipt":
    st.title("📸 Upload Receipt")
    st.markdown("Upload a receipt image and Gemini AI will extract the details automatically.")
    
    uploaded_file = st.file_uploader(
        "Choose a receipt image",
        type=['png', 'jpg', 'jpeg'],
        help="Upload a clear image of your receipt"
    )
    
    if uploaded_file:
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
        
        with col2:
            if st.button("🤖 Extract with Gemini AI", type="primary", use_container_width=True):
                with st.spinner("🔍 Analyzing receipt with Gemini Vision..."):
                    image_bytes = uploaded_file.getvalue()
                    data, error = extract_receipt_with_gemini(image_bytes)
                    
                    if error:
                        st.error(f"❌ {error}")
                    elif data:
                        st.success("✅ Receipt analyzed successfully!")
                        
                        # Display extracted data
                        st.json(data)
                        
                        # Confirm and add
                        st.divider()
                        st.subheader("📝 Confirm Transaction")
                        
                        with st.form("confirm_receipt"):
                            c_merchant = st.text_input("Merchant", value=data.get('merchant', 'Unknown'))
                            c_amount = st.number_input("Amount", value=float(data.get('amount', 0)), format="%.2f")
                            c_category = st.selectbox("Category", EXPENSE_CATEGORIES, 
                                                     index=EXPENSE_CATEGORIES.index(data.get('category', 'Other')))
                            c_date = st.date_input("Date", value=datetime.strptime(data.get('date', str(datetime.now().date())), "%Y-%m-%d"))
                            c_items = st.text_area("Items", value=", ".join(data.get('items', [])))
                            
                            if st.form_submit_button("✅ Add Transaction", use_container_width=True):
                                new_trans = {
                                    "id": str(uuid.uuid4()),
                                    "type": "Expense",
                                    "amount": float(c_amount),
                                    "category": c_category,
                                    "date": str(c_date),
                                    "merchant": c_merchant,
                                    "notes": f"Items: {c_items}" if c_items else "Receipt upload"
                                }
                                st.session_state.transactions.insert(0, new_trans)
                                st.success("✅ Transaction added from receipt!")
                                st.rerun()

# ============================================================================
# CHAT WITH PILOT PAGE - COMPLETE FIX
# ============================================================================
elif page == "Chat with Pilot":
    st.title("🤖 Chat with Pilot")
    
    # Info box with financial summary
    total_income, total_expenses, balance = get_summary()
    
    st.markdown(f"""
    <div class="info-box">
        <h3 style="margin-top:0;">👋 Hi! I'm Pilot, your AI finance assistant</h3>
        <p>I can help you understand your spending, create budgets, and give personalized financial advice.</p>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px;">
            <div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Balance</div>
                <div style="font-size: 1.5rem; font-weight: 600;">₹{balance:,.2f}</div>
            </div>
            <div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Income</div>
                <div style="font-size: 1.5rem; font-weight: 600;">₹{total_income:,.2f}</div>
            </div>
            <div>
                <div style="font-size: 0.9rem; opacity: 0.9;">Expenses</div>
                <div style="font-size: 1.5rem; font-weight: 600;">₹{total_expenses:,.2f}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Quick query suggestions
    st.markdown("### 💡 Quick Questions")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✨ How much did I spend on food?", use_container_width=True):
            handle_quick_query("How much did I spend on food this month?")
            st.rerun()
        if st.button("✨ Give me 3 money-saving tips", use_container_width=True):
            handle_quick_query("Give me 3 simple tips to save money as a student")
            st.rerun()
    
    with col2:
        if st.button("✨ What's my biggest expense?", use_container_width=True):
            handle_quick_query("What's my biggest expense category and how can I reduce it?")
            st.rerun()
        if st.button("✨ Summarize my spending", use_container_width=True):
            handle_quick_query("Give me a summary of my spending this month")
            st.rerun()
    
    st.divider()
    
    # Chat history display - FIX: Proper rendering with visibility
    st.markdown("### 💬 Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.chat_history:
            st.info("👋 Start a conversation by asking a question below or clicking a suggestion above!")
        else:
            # Render all messages
            for idx, msg in enumerate(st.session_state.chat_history):
                if msg["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <div class="message-label">You</div>
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="assistant-message">
                        <div class="message-label">🤖 Pilot</div>
                        {msg["content"]}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Add some spacing
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Chat input - FIX: Proper event handling with on_change callback
    st.text_input(
        "Ask Pilot about your finances...",
        key="chat_input_field",
        placeholder="e.g., How can I save more money this month?",
        on_change=handle_chat_submit,
        label_visibility="collapsed"
    )
    
    # Alternative: Manual send button for users who prefer clicking
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("🚀 Send", type="primary", use_container_width=True, disabled=st.session_state.processing):
            handle_chat_submit()
            st.rerun()
    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Show processing indicator
    if st.session_state.processing:
        with st.spinner("🤔 Pilot is thinking..."):
            pass

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
    <p>💰 PocketPilot AI - Smart Finance for Students | Powered by Gemini 1.5 Flash</p>
</div>
""", unsafe_allow_html=True)