import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import json
import sys

# Add parent directory to path to import services
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import custom services
<<<<<<< HEAD
try:
    from services.gemini_service import GeminiClient, get_quick_insight
    GEMINI_AVAILABLE = True
except Exception as e:
    GEMINI_AVAILABLE = False
    print(f"Gemini service not available: {e}")

try:
    from services.document_service import DocumentAIClient, MockDocumentAIClient
=======
GEMINI_AVAILABLE = False
DOCUMENT_AI_AVAILABLE = False
GeminiClient = None
DocumentAIClient = None
MockDocumentAIClient = None

try:
    from services.gemini_service import GeminiClient
    GEMINI_AVAILABLE = True
    print("✓ Gemini service loaded successfully")
except ImportError as e:
    print(f"⚠ Gemini service not available: {e}")
    try:
        from services.gemini_client import GeminiClient
        GEMINI_AVAILABLE = True
        print("✓ Gemini service loaded successfully (alternate path)")
    except ImportError as e2:
        print(f"⚠ Gemini service not available: {e2}")

try:
    from services.document_ai_service import DocumentAIClient, MockDocumentAIClient
>>>>>>> b5e463fac8599b7221b8ad005e25a964a8be5249
    DOCUMENT_AI_AVAILABLE = True
    print("✓ Document AI service loaded successfully")
except ImportError as e:
    print(f"⚠ Document AI service not available: {e}")
    try:
        from services.document_ai import DocumentAIClient, MockDocumentAIClient
        DOCUMENT_AI_AVAILABLE = True
        print("✓ Document AI service loaded successfully (alternate path)")
    except ImportError as e2:
        print(f"⚠ Document AI service not available: {e2}")

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="PocketPilot AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #4F46E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 0.5rem;
        font-weight: 600;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #E0E7FF;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #F3F4F6;
        margin-right: 20%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'transactions' not in st.session_state:
    st.session_state.transactions = pd.DataFrame(
        columns=['id', 'type', 'amount', 'category', 'date', 'merchant', 'notes', 'timestamp']
    )
    # Add some sample data for demo
    sample_data = [
        {'id': 1, 'type': 'Expense', 'amount': 250.00, 'category': 'Food', 'date': datetime.now() - timedelta(days=2), 'merchant': 'Restaurant ABC', 'notes': 'Lunch with friends', 'timestamp': datetime.now()},
        {'id': 2, 'type': 'Expense', 'amount': 50.00, 'category': 'Transport', 'date': datetime.now() - timedelta(days=1), 'merchant': 'Uber', 'notes': 'Ride to college', 'timestamp': datetime.now()},
        {'id': 3, 'type': 'Income', 'amount': 5000.00, 'category': 'Allowance', 'date': datetime.now() - timedelta(days=5), 'merchant': 'Parent Transfer', 'notes': 'Monthly allowance', 'timestamp': datetime.now()},
    ]
    st.session_state.transactions = pd.DataFrame(sample_data)

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'api_keys' not in st.session_state:
    st.session_state.api_keys = {
        'gemini': os.getenv('GOOGLE_API_KEY', ''),
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT', ''),
        'processor_id': os.getenv('DOCUMENT_AI_PROCESSOR_ID', '')
    }

if 'gemini_client' not in st.session_state and GEMINI_AVAILABLE:
    try:
        api_key = st.session_state.api_keys.get('gemini') or os.getenv('GOOGLE_API_KEY')
        if api_key:
            st.session_state.gemini_client = GeminiClient(api_key)
        else:
            st.session_state.gemini_client = None
    except Exception as e:
        st.session_state.gemini_client = None
        print(f"Failed to initialize Gemini client: {e}")

if 'document_ai_client' not in st.session_state and DOCUMENT_AI_AVAILABLE:
    try:
        project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        processor_id = os.getenv('DOCUMENT_AI_PROCESSOR_ID')
        
        if project_id and processor_id:
            st.session_state.document_ai_client = DocumentAIClient(
                project_id=project_id,
                processor_id=processor_id
            )
        else:
            # Use mock client for demo
            st.session_state.document_ai_client = MockDocumentAIClient()
    except Exception as e:
        st.session_state.document_ai_client = MockDocumentAIClient()
        print(f"Using Mock Document AI client: {e}")

# Helper functions
def add_transaction(transaction_data):
    """Add a new transaction to the dataframe"""
    new_id = len(st.session_state.transactions) + 1
    transaction_data['id'] = new_id
    transaction_data['timestamp'] = datetime.now()
    st.session_state.transactions = pd.concat(
        [st.session_state.transactions, pd.DataFrame([transaction_data])],
        ignore_index=True
    )

def delete_transaction(transaction_id):
    """Delete a transaction by ID"""
    st.session_state.transactions = st.session_state.transactions[
        st.session_state.transactions['id'] != transaction_id
    ]

def calculate_summary():
    """Calculate financial summary"""
    df = st.session_state.transactions.copy()
    if df.empty:
        return {'total_income': 0, 'total_expenses': 0, 'balance': 0}
    
    total_income = df[df['type'] == 'Income']['amount'].sum()
    total_expenses = df[df['type'] == 'Expense']['amount'].sum()
    balance = total_income - total_expenses
    
    return {
        'total_income': total_income,
        'total_expenses': total_expenses,
        'balance': balance
    }

def get_category_summary():
    """Get spending by category"""
    df = st.session_state.transactions.copy()
    expenses = df[df['type'] == 'Expense']
    if expenses.empty:
        return pd.DataFrame()
    return expenses.groupby('category')['amount'].sum().sort_values(ascending=False)

# Sidebar Navigation
st.sidebar.markdown('<h1 style="color: #4F46E5;">💰 PocketPilot AI</h1>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# API Configuration Section
with st.sidebar.expander("⚙️ API Configuration", expanded=not st.session_state.get('gemini_client')):
    st.markdown("#### Gemini AI")
    gemini_key = st.text_input(
        "API Key",
        value=st.session_state.api_keys.get('gemini', ''),
        type="password",
        key="gemini_api_input",
        help="Get your key from https://makersuite.google.com/app/apikey"
    )
    
    if st.button("💾 Save Gemini Key", use_container_width=True):
        if gemini_key:
            st.session_state.api_keys['gemini'] = gemini_key
            if not GEMINI_AVAILABLE:
                st.error("❌ Gemini service files not found. Please check services/gemini_client.py exists.")
            else:
                try:
                    st.session_state.gemini_client = GeminiClient(gemini_key)
                    st.success("✅ Gemini API connected!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to connect: {str(e)}")
        else:
            st.error("Please enter an API key")
    
    st.markdown("---")
    st.markdown("#### Document AI (Optional)")
    project_id = st.text_input(
        "Project ID",
        value=st.session_state.api_keys.get('project_id', ''),
        key="project_id_input"
    )
    processor_id = st.text_input(
        "Processor ID",
        value=st.session_state.api_keys.get('processor_id', ''),
        key="processor_id_input"
    )
    
    if st.button("💾 Save Document AI Config", use_container_width=True):
        if project_id and processor_id:
            st.session_state.api_keys['project_id'] = project_id
            st.session_state.api_keys['processor_id'] = processor_id
            if not DOCUMENT_AI_AVAILABLE:
                st.warning("⚠ Document AI service not found. Check services/document_ai.py exists.")
            else:
                try:
                    st.session_state.document_ai_client = DocumentAIClient(
                        project_id=project_id,
                        processor_id=processor_id
                    )
                    st.success("✅ Document AI connected!")
                    st.rerun()
                except Exception as e:
                    st.warning(f"Using mock mode: {str(e)}")
                    if MockDocumentAIClient:
                        st.session_state.document_ai_client = MockDocumentAIClient()
        else:
            st.info("Using demo mode for Document AI")
            if MockDocumentAIClient:
                st.session_state.document_ai_client = MockDocumentAIClient()

st.sidebar.markdown("---")

# API Status indicators
st.sidebar.markdown("### 🔌 API Status")
gemini_status = "🟢 Connected" if st.session_state.get('gemini_client') else "🔴 Not configured"
doc_ai_status = "🟢 Connected" if st.session_state.get('document_ai_client') and not isinstance(st.session_state.document_ai_client, MockDocumentAIClient) else "🟡 Demo Mode"
st.sidebar.markdown(f"**Gemini AI:** {gemini_status}")
st.sidebar.markdown(f"**Document AI:** {doc_ai_status}")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "➕ Add Transaction", "📋 Transactions", "📸 Upload Receipt", "🤖 AI Pilot Chat", "📈 Analytics"]
)

# Main content based on page selection
if page == "📊 Dashboard":
    st.markdown('<p class="main-header">💰 Financial Dashboard</p>', unsafe_allow_html=True)
    
    # Summary metrics
    summary = calculate_summary()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            label="💵 Total Income",
            value=f"₹{summary['total_income']:,.2f}",
            delta="This period"
        )
    with col2:
        st.metric(
            label="💸 Total Expenses",
            value=f"₹{summary['total_expenses']:,.2f}",
            delta=f"-₹{summary['total_expenses']:,.2f}"
        )
    with col3:
        balance_delta = summary['balance']
        st.metric(
            label="💰 Balance",
            value=f"₹{summary['balance']:,.2f}",
            delta=f"₹{balance_delta:,.2f}" if balance_delta >= 0 else f"-₹{abs(balance_delta):,.2f}"
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Spending by Category")
        category_data = get_category_summary()
        if not category_data.empty:
            fig = px.pie(
                values=category_data.values,
                names=category_data.index,
                title="Expense Distribution",
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expense data to display")
    
    with col2:
        st.subheader("📈 Recent Transactions")
        df = st.session_state.transactions.copy()
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            recent = df.sort_values('date', ascending=False).head(10)
            
            fig = go.Figure()
            expenses = recent[recent['type'] == 'Expense']
            income = recent[recent['type'] == 'Income']
            
            fig.add_trace(go.Bar(
                x=expenses['date'],
                y=expenses['amount'],
                name='Expenses',
                marker_color='#EF4444'
            ))
            fig.add_trace(go.Bar(
                x=income['date'],
                y=income['amount'],
                name='Income',
                marker_color='#10B981'
            ))
            
            fig.update_layout(
                title="Income vs Expenses",
                barmode='group',
                xaxis_title="Date",
                yaxis_title="Amount (₹)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No transaction data to display")

elif page == "➕ Add Transaction":
    st.markdown('<p class="main-header">➕ Add New Transaction</p>', unsafe_allow_html=True)
    
    with st.form("transaction_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            trans_type = st.selectbox("Type", ["Expense", "Income"])
            amount = st.number_input("Amount (₹)", min_value=0.0, step=10.0, format="%.2f")
            category = st.selectbox(
                "Category",
                ["Food", "Transport", "Groceries", "Bills", "Entertainment", "Education", "Health", "Shopping", "Allowance", "Salary", "Others"]
            )
        
        with col2:
            date = st.date_input("Date", value=datetime.today())
            merchant = st.text_input("Merchant/Source")
            notes = st.text_area("Notes (Optional)")
        
        submitted = st.form_submit_button("💾 Add Transaction", use_container_width=True)
        
        if submitted:
            if amount > 0:
                transaction_data = {
                    'type': trans_type,
                    'amount': amount,
                    'category': category,
                    'date': pd.to_datetime(date),
                    'merchant': merchant,
                    'notes': notes
                }
                add_transaction(transaction_data)
                st.success(f"✅ {trans_type} of ₹{amount:,.2f} added successfully!")
                st.balloons()
            else:
                st.error("❌ Amount must be greater than 0")

elif page == "📋 Transactions":
    st.markdown('<p class="main-header">📋 Transaction History</p>', unsafe_allow_html=True)
    
    df = st.session_state.transactions.copy()
    
    if not df.empty:
        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            filter_type = st.multiselect("Filter by Type", ["Expense", "Income"], default=["Expense", "Income"])
        with col2:
            categories = df['category'].unique().tolist()
            filter_category = st.multiselect("Filter by Category", categories, default=categories)
        with col3:
            sort_by = st.selectbox("Sort by", ["Date (Newest)", "Date (Oldest)", "Amount (High to Low)", "Amount (Low to High)"])
        
        # Apply filters
        filtered_df = df[
            (df['type'].isin(filter_type)) &
            (df['category'].isin(filter_category))
        ].copy()
        
        # Apply sorting
        if sort_by == "Date (Newest)":
            filtered_df = filtered_df.sort_values('date', ascending=False)
        elif sort_by == "Date (Oldest)":
            filtered_df = filtered_df.sort_values('date', ascending=True)
        elif sort_by == "Amount (High to Low)":
            filtered_df = filtered_df.sort_values('amount', ascending=False)
        else:
            filtered_df = filtered_df.sort_values('amount', ascending=True)
        
        # Display transactions
        st.markdown(f"### Showing {len(filtered_df)} transactions")
        
        for idx, row in filtered_df.iterrows():
            with st.expander(f"{'🔴' if row['type'] == 'Expense' else '🟢'} ₹{row['amount']:,.2f} - {row['category']} - {row['date'].strftime('%Y-%m-%d')}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**Merchant/Source:** {row['merchant']}")
                    st.write(f"**Date:** {row['date'].strftime('%Y-%m-%d')}")
                    st.write(f"**Notes:** {row['notes'] if row['notes'] else 'N/A'}")
                with col2:
                    if st.button(f"🗑️ Delete", key=f"del_{row['id']}"):
                        delete_transaction(row['id'])
                        st.rerun()
        
        # Export button
        st.markdown("---")
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Export to CSV",
            data=csv,
            file_name=f"transactions_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    else:
        st.info("📭 No transactions yet. Add your first transaction to get started!")

elif page == "📸 Upload Receipt":
    st.markdown('<p class="main-header">📸 Upload Receipt</p>', unsafe_allow_html=True)
    
    # Check Document AI availability
    if not st.session_state.get('document_ai_client'):
        st.warning("⚠️ Document AI is not configured. Using demo mode.")
        st.info("""
        **To enable real Document AI:**
        1. Set `GOOGLE_CLOUD_PROJECT` in .env
        2. Set `DOCUMENT_AI_PROCESSOR_ID` in .env
        3. Restart the app
        """)
    
    uploaded_file = st.file_uploader(
        "Choose a receipt image or PDF",
        type=['jpg', 'jpeg', 'png', 'pdf'],
        help="Upload a clear image of your receipt for automatic data extraction"
    )
    
    if uploaded_file is not None:
        # Display uploaded file
        if uploaded_file.type.startswith('image'):
            st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
        else:
            st.info(f"📄 PDF uploaded: {uploaded_file.name}")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            process_button = st.button("🔍 Extract Details", use_container_width=True, type="primary")
        with col2:
            use_mock = st.checkbox("Demo Mode", value=True, help="Use demo data for testing")
        
        if process_button:
            with st.spinner("🔄 Processing receipt with Document AI..."):
                try:
                    # Read file content
                    file_content = uploaded_file.read()
                    
                    # Determine MIME type
                    if uploaded_file.type == 'application/pdf':
                        mime_type = 'application/pdf'
                    elif 'png' in uploaded_file.type:
                        mime_type = 'image/png'
                    else:
                        mime_type = 'image/jpeg'
                    
                    # Process with Document AI
                    client = st.session_state.document_ai_client
                    result = client.process_receipt(file_content, mime_type)
                    
                    if result['success']:
                        st.success("✅ Receipt processed successfully!")
                        
                        extracted = result['data']
                        
                        # Display extracted data
                        st.markdown("### 📋 Extracted Information")
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Amount", f"₹{extracted['amount']:.2f}" if extracted['amount'] else "Not found")
                        with col2:
                            st.metric("Merchant", extracted['merchant'] if extracted['merchant'] else "Not found")
                        with col3:
                            st.metric("Category", extracted['category'])
                        
                        if extracted['date']:
                            st.write(f"**Date:** {extracted['date'].strftime('%Y-%m-%d')}")
                        
                        st.write(f"**Confidence Score:** {result['confidence']:.1%}")
                        
                        # Show items if available
                        if extracted['items']:
                            st.markdown("**Items Found:**")
                            for item in extracted['items'][:5]:  # Show first 5 items
                                st.write(f"- {item['name']}")
                        
                        # Validation
                        is_valid, issues = client.validate_extraction(extracted)
                        
                        if not is_valid:
                            st.warning("⚠️ Some information is missing or unclear:")
                            for issue in issues:
                                st.write(f"- {issue}")
                        
                        st.markdown("---")
                        
                        # Form to review and add transaction
                        st.markdown("### ✏️ Review & Add Transaction")
                        
                        with st.form("receipt_transaction_form"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                final_amount = st.number_input(
                                    "Amount (₹)",
                                    value=float(extracted['amount']) if extracted['amount'] else 0.0,
                                    min_value=0.0,
                                    step=10.0
                                )
                                final_merchant = st.text_input(
                                    "Merchant",
                                    value=extracted['merchant'] if extracted['merchant'] else ""
                                )
                                final_category = st.selectbox(
                                    "Category",
                                    ["Food", "Transport", "Groceries", "Bills", "Entertainment", "Education", "Health", "Shopping", "Others"],
                                    index=["Food", "Transport", "Groceries", "Bills", "Entertainment", "Education", "Health", "Shopping", "Others"].index(extracted['category']) if extracted['category'] in ["Food", "Transport", "Groceries", "Bills", "Entertainment", "Education", "Health", "Shopping", "Others"] else 8
                                )
                            
                            with col2:
                                final_date = st.date_input(
                                    "Date",
                                    value=extracted['date'] if extracted['date'] else datetime.today()
                                )
                                final_notes = st.text_area(
                                    "Notes",
                                    value=f"Auto-extracted from receipt. Confidence: {result['confidence']:.1%}"
                                )
                            
                            submitted = st.form_submit_button("💾 Add Transaction", use_container_width=True)
                            
                            if submitted:
                                if final_amount > 0:
                                    transaction_data = {
                                        'type': 'Expense',
                                        'amount': final_amount,
                                        'category': final_category,
                                        'date': pd.to_datetime(final_date),
                                        'merchant': final_merchant,
                                        'notes': final_notes
                                    }
                                    add_transaction(transaction_data)
                                    st.success(f"✅ Transaction of ₹{final_amount:,.2f} added successfully!")
                                    st.balloons()
                                else:
                                    st.error("❌ Amount must be greater than 0")
                    
                    else:
                        st.error(f"❌ Failed to process receipt: {result.get('error', 'Unknown error')}")
                        st.info("Please try with a clearer image or add the transaction manually.")
                
                except Exception as e:
                    st.error(f"❌ Error processing receipt: {str(e)}")
                    st.info("Please add the transaction manually from the 'Add Transaction' page.")

elif page == "🤖 AI Pilot Chat":
    st.markdown('<p class="main-header">🤖 AI Pilot Assistant</p>', unsafe_allow_html=True)
    
    # Check Gemini availability
    if not st.session_state.get('gemini_client'):
        st.error("❌ Gemini API is not configured!")
        
        st.markdown("### 🔑 Quick Setup")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            quick_api_key = st.text_input(
                "Enter your Gemini API Key",
                type="password",
                placeholder="AIza...",
                help="Get your key from https://makersuite.google.com/app/apikey"
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Connect Now", use_container_width=True, type="primary"):
                if quick_api_key:
                    st.session_state.api_keys['gemini'] = quick_api_key
                    try:
                        st.session_state.gemini_client = GeminiClient(quick_api_key)
                        st.success("✅ Connected!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("Please enter an API key")
        
        st.info("""
        **Steps to get your API key:**
        1. Visit https://makersuite.google.com/app/apikey
        2. Click "Create API Key in new project" (or select existing project)
        3. Copy the API key
        4. Paste it above and click "Connect Now"
        """)
        
        # Show demo interface
        st.markdown("---")
        st.markdown("### 💡 Demo Mode - Sample Insights")
        
        summary = calculate_summary()
        category_summary = get_category_summary()
        
        demo_response = f"""Based on your transaction data, here's what I can see:

📊 **Financial Overview:**
- Total Income: ₹{summary['total_income']:,.2f}
- Total Expenses: ₹{summary['total_expenses']:,.2f}
- Current Balance: ₹{summary['balance']:,.2f}

💡 **Quick Insights:**
1. Your top spending category is {category_summary.index[0] if not category_summary.empty else 'N/A'}
2. You're spending ₹{category_summary.iloc[0] if not category_summary.empty else 0:,.2f} in this category
3. Consider the 50-30-20 budget rule for better financial health

🎯 **Recommendations:**
- Track daily expenses to identify patterns
- Set category-wise monthly budgets
- Try to save at least 20% of your income

*Connect Gemini API above for personalized, AI-powered insights!*
"""
        st.markdown(demo_response)
        
    else:
        st.info("💡 Ask me about your spending habits, get budget advice, or request financial insights!")
        
        # Display chat history
        chat_container = st.container()
        
        with chat_container:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-message assistant-message"><strong>🤖 Pilot:</strong><br>{message["content"]}</div>', unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown("### 🎯 Quick Actions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Spending Summary", use_container_width=True):
                st.session_state.quick_query = "Give me a summary of my spending this month"
        with col2:
            if st.button("💡 Budget Tips", use_container_width=True):
                st.session_state.quick_query = "Give me 5 actionable tips to reduce my expenses"
        with col3:
            if st.button("📈 Trend Analysis", use_container_width=True):
                st.session_state.quick_query = "Analyze my spending trends and patterns"
        
        # Chat input
        user_input = st.text_input(
            "Ask Pilot a question:",
            key="chat_input",
            placeholder="e.g., How much did I spend on food this month?",
            value=st.session_state.get('quick_query', '')
        )
        
        # Clear quick query after use
        if 'quick_query' in st.session_state:
            del st.session_state.quick_query
        
        col1, col2 = st.columns([4, 1])
        with col1:
            send_button = st.button("💬 Send", use_container_width=True, type="primary")
        with col2:
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()
        
        if send_button and user_input:
            # Add user message
            st.session_state.chat_history.append({'role': 'user', 'content': user_input})
            
            # Generate AI response
            with st.spinner("🤔 Pilot is thinking..."):
                try:
                    client = st.session_state.gemini_client
                    df = st.session_state.transactions.copy()
                    
                    response = client.get_financial_insights(df, user_input)
                    
                    st.session_state.chat_history.append({'role': 'assistant', 'content': response})
                    st.rerun()
                    
                except Exception as e:
                    error_msg = f"⚠️ Sorry, I encountered an error: {str(e)}\n\nPlease check your API key and try again."
                    st.session_state.chat_history.append({'role': 'assistant', 'content': error_msg})
                    st.rerun()

elif page == "📈 Analytics":
    st.markdown('<p class="main-header">📈 Advanced Analytics</p>', unsafe_allow_html=True)
    
    df = st.session_state.transactions.copy()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        
        # Time period selector
        period = st.selectbox("Select Time Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
        
        # Filter by period
        today = datetime.now()
        if period == "Last 7 Days":
            start_date = today - timedelta(days=7)
        elif period == "Last 30 Days":
            start_date = today - timedelta(days=30)
        elif period == "Last 90 Days":
            start_date = today - timedelta(days=90)
        else:
            start_date = df['date'].min()
        
        filtered_df = df[df['date'] >= start_date]
        
        # Summary for period
        period_summary = {
            'income': filtered_df[filtered_df['type'] == 'Income']['amount'].sum(),
            'expenses': filtered_df[filtered_df['type'] == 'Expense']['amount'].sum()
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Income", f"₹{period_summary['income']:,.2f}")
        with col2:
            st.metric("Expenses", f"₹{period_summary['expenses']:,.2f}")
        with col3:
            savings_rate = ((period_summary['income'] - period_summary['expenses']) / period_summary['income'] * 100) if period_summary['income'] > 0 else 0
            st.metric("Savings Rate", f"{savings_rate:.1f}%")
        
        # Daily trend
        st.subheader("📅 Daily Spending Trend")
        daily_expenses = filtered_df[filtered_df['type'] == 'Expense'].groupby(filtered_df['date'].dt.date)['amount'].sum().reset_index()
        fig = px.line(daily_expenses, x='date', y='amount', title='Daily Expenses', markers=True)
        fig.update_layout(xaxis_title="Date", yaxis_title="Amount (₹)")
        st.plotly_chart(fig, use_container_width=True)
        
        # Category breakdown
        st.subheader("🎯 Top Spending Categories")
        category_data = get_category_summary()
        if not category_data.empty:
            fig = px.bar(
                x=category_data.values,
                y=category_data.index,
                orientation='h',
                title='Spending by Category',
                labels={'x': 'Amount (₹)', 'y': 'Category'}
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("📭 No data available for analytics. Start adding transactions!")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Tech Stack")
st.sidebar.markdown("- Streamlit (UI)")
st.sidebar.markdown("- Gemini API (AI)")
st.sidebar.markdown("- Document AI (OCR)")
st.sidebar.markdown("- Pandas (Analytics)")
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ for hackathon")
st.sidebar.markdown("**PocketPilot AI** v1.0")
