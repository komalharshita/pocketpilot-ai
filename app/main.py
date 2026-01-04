import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
import json

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
    
    st.info("🚀 **Coming Soon:** Upload receipts and let Document AI extract transaction details automatically!")
    
    uploaded_file = st.file_uploader("Choose a receipt image or PDF", type=['jpg', 'jpeg', 'png', 'pdf'])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Receipt", use_column_width=True)
        
        if st.button("🔍 Extract Details", use_container_width=True):
            with st.spinner("Processing receipt with Document AI..."):
                # Placeholder for Document AI integration
                st.warning("⚠️ Document AI integration in progress. For now, please add transactions manually.")
                st.info("""
                **Next Steps:**
                1. Set up Google Cloud Project
                2. Enable Document AI API
                3. Create a processor for receipts
                4. Add credentials to .env file
                """)

elif page == "🤖 AI Pilot Chat":
    st.markdown('<p class="main-header">🤖 AI Pilot Assistant</p>', unsafe_allow_html=True)
    
    st.info("💡 Ask me about your spending habits, get budget advice, or request financial insights!")
    
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f"**You:** {message['content']}")
            else:
                st.markdown(f"**🤖 Pilot:** {message['content']}")
    
    # Chat input
    user_input = st.text_input("Ask Pilot a question:", key="chat_input")
    
    if st.button("Send", use_container_width=True) and user_input:
        # Add user message
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # Generate AI response (placeholder)
        summary = calculate_summary()
        category_summary = get_category_summary()
        
        # Simple rule-based responses for demo
        response = f"""Based on your recent transactions:
        
📊 **Your Financial Summary:**
- Total Income: ₹{summary['total_income']:,.2f}
- Total Expenses: ₹{summary['total_expenses']:,.2f}
- Current Balance: ₹{summary['balance']:,.2f}

💡 **Quick Tips:**
1. Your biggest expense category is {category_summary.index[0] if not category_summary.empty else 'N/A'}
2. Try to maintain a 50-30-20 budget rule (50% needs, 30% wants, 20% savings)
3. Consider setting aside ₹{summary['total_income'] * 0.2:,.2f} for savings this month

🎯 **Action Items:**
- Track daily expenses to identify spending patterns
- Set category-wise budgets
- Review your spending weekly

*Note: Connect Gemini API for more personalized insights!*
"""
        
        st.session_state.chat_history.append({'role': 'assistant', 'content': response})
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