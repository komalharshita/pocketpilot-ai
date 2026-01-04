"""
PocketPilot AI - Rebuilt from Scratch
A simple receipt management system with AI assistance

Core Features:
1. Dashboard - View all receipts
2. Receipt Upload - Upload and extract data with Document AI
3. AI Chat - Chat with Gemini about your receipts
"""

import streamlit as st
from datetime import datetime
import uuid

# Import our services
from services.firebase_service import FirebaseService
from services.document_service import DocumentAIService
from services.gemini_service import GeminiService

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title="PocketPilot AI - Finance Dashboard",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# CUSTOM STYLES
# ============================================================================
st.markdown("""
<style>
    /* Clean, minimal design */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Receipt card */
    .receipt-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 16px;
    }
    
    /* Chat messages */
    .user-msg {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0;
        margin-left: 20%;
    }
    
    .ai-msg {
        background: #f1f3f5;
        color: #212529;
        padding: 12px 16px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 0;
        margin-right: 20%;
        border-left: 3px solid #667eea;
    }
    
    /* Stats cards */
    .stat-card {
        background: white;
        padding: 16px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INITIALIZE SERVICES
# ============================================================================

@st.cache_resource
def init_services():
    """Initialize all services once"""
    try:
        firebase = FirebaseService()
        document_ai = DocumentAIService()
        gemini = GeminiService()
        return firebase, document_ai, gemini
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        return None, None, None

firebase_service, document_ai_service, gemini_service = init_services()

# ============================================================================
# SESSION STATE
# ============================================================================
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================
st.sidebar.title("🧾 PocketPilot AI")
st.sidebar.markdown("*Simple Receipt Management*")

# Check service status
if firebase_service and document_ai_service and gemini_service:
    st.sidebar.success("✅ All services connected")
else:
    st.sidebar.error("⚠️ Some services unavailable")

st.sidebar.divider()

page = st.sidebar.radio(
    "Navigate",
    ["📊 Dashboard", "📤 Upload Receipt", "💬 AI Assistant"],
    label_visibility="collapsed"
)

# ============================================================================
# PAGE 1: DASHBOARD
# ============================================================================
if page == "📊 Dashboard":
    st.title("📊 Receipt Dashboard")
    st.markdown("View all your uploaded receipts and summaries")
    
    if not firebase_service:
        st.error("Firebase service unavailable. Please check configuration.")
    else:
        # Fetch all receipts
        with st.spinner("Loading receipts..."):
            receipts = firebase_service.get_all_receipts()
        
        if not receipts:
            st.info("📭 No receipts yet. Upload your first receipt to get started!")
        else:
            # Summary statistics
            st.subheader("📈 Summary")
            col1, col2, col3 = st.columns(3)
            
            total_receipts = len(receipts)
            total_amount = sum(r.get('amount', 0) for r in receipts if r.get('amount'))
            avg_amount = total_amount / total_receipts if total_receipts > 0 else 0
            
            with col1:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">{total_receipts}</div>
                    <div class="stat-label">Total Receipts</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">₹{total_amount:,.2f}</div>
                    <div class="stat-label">Total Amount</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="stat-card">
                    <div class="stat-value">₹{avg_amount:,.2f}</div>
                    <div class="stat-label">Average Amount</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.divider()
            
            # Display receipts
            st.subheader("🧾 All Receipts")
            
            # Sort by date (newest first)
            receipts_sorted = sorted(
                receipts, 
                key=lambda x: x.get('uploaded_at', ''), 
                reverse=True
            )
            
            for receipt in receipts_sorted:
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        merchant = receipt.get('merchant', 'Unknown Merchant')
                        amount = receipt.get('amount', 0)
                        date = receipt.get('date', 'N/A')
                        
                        st.markdown(f"""
                        <div class="receipt-card">
                            <h4>🏪 {merchant}</h4>
                            <p><strong>Amount:</strong> ₹{amount:,.2f}</p>
                            <p><strong>Date:</strong> {date}</p>
                            <p><strong>Uploaded:</strong> {receipt.get('uploaded_at', 'N/A')}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        # Show image if available
                        if receipt.get('image_url'):
                            if st.button("🖼️ View", key=f"view_{receipt['id']}"):
                                st.image(receipt['image_url'], caption=merchant, width=200)
                        
                        # Delete button
                        if st.button("🗑️ Delete", key=f"del_{receipt['id']}"):
                            firebase_service.delete_receipt(receipt['id'])
                            st.success("Receipt deleted!")
                            st.rerun()

# ============================================================================
# PAGE 2: UPLOAD RECEIPT
# ============================================================================
elif page == "📤 Upload Receipt":
    st.title("📤 Upload Receipt")
    st.markdown("Upload a receipt image or PDF for automatic data extraction")
    
    if not firebase_service or not document_ai_service:
        st.error("Services unavailable. Please check configuration.")
    else:
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a receipt file",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Upload a clear image or PDF of your receipt"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.subheader("📄 Preview")
                if uploaded_file.type.startswith('image'):
                    st.image(uploaded_file, use_column_width=True)
                else:
                    st.info("📑 PDF uploaded. Processing...")
            
            with col2:
                st.subheader("🤖 Extract Data")
                
                if st.button("🚀 Process Receipt", type="primary", use_container_width=True):
                    with st.spinner("🔍 Extracting data with Document AI..."):
                        # Read file bytes
                        file_bytes = uploaded_file.read()
                        mime_type = uploaded_file.type
                        
                        # Extract data using Document AI
                        extracted_data = document_ai_service.extract_receipt_data(
                            file_bytes, 
                            mime_type
                        )
                        
                        if extracted_data.get('success'):
                            data = extracted_data['data']
                            
                            st.success("✅ Data extracted successfully!")
                            
                            # Display extracted data
                            st.json(data)
                            
                            # Confirmation form
                            st.divider()
                            st.subheader("✏️ Confirm & Save")
                            
                            with st.form("confirm_receipt"):
                                merchant = st.text_input(
                                    "Merchant", 
                                    value=data.get('merchant', '')
                                )
                                amount = st.number_input(
                                    "Amount (₹)", 
                                    value=float(data.get('amount', 0)),
                                    min_value=0.0,
                                    format="%.2f"
                                )
                                date = st.text_input(
                                    "Date", 
                                    value=data.get('date', str(datetime.now().date()))
                                )
                                items = st.text_area(
                                    "Items (comma-separated)",
                                    value=", ".join(data.get('items', []))
                                )
                                
                                submitted = st.form_submit_button(
                                    "💾 Save Receipt",
                                    use_container_width=True
                                )
                                
                                if submitted:
                                    # Upload file to Firebase Storage
                                    file_url = firebase_service.upload_file(
                                        file_bytes,
                                        uploaded_file.name,
                                        mime_type
                                    )
                                    
                                    # Save receipt data to Firestore
                                    receipt_id = str(uuid.uuid4())
                                    receipt_data = {
                                        'id': receipt_id,
                                        'merchant': merchant,
                                        'amount': amount,
                                        'date': date,
                                        'items': [i.strip() for i in items.split(',') if i.strip()],
                                        'image_url': file_url,
                                        'uploaded_at': datetime.now().isoformat(),
                                        'raw_data': data
                                    }
                                    
                                    firebase_service.save_receipt(receipt_data)
                                    
                                    st.success("✅ Receipt saved successfully!")
                                    st.balloons()
                                    
                                    # Reset file uploader
                                    if st.button("📤 Upload Another"):
                                        st.rerun()
                        else:
                            st.error(f"❌ Extraction failed: {extracted_data.get('error')}")

# ============================================================================
# PAGE 3: AI ASSISTANT
# ============================================================================
elif page == "💬 AI Assistant":
    st.title("💬 AI Assistant")
    st.markdown("Chat with AI about your receipts and expenses")
    
    if not gemini_service:
        st.error("Gemini service unavailable. Please check API key.")
    else:
        # Get receipts for context
        receipts = firebase_service.get_all_receipts() if firebase_service else []
        
        # Info box
        st.info(f"💡 I have access to {len(receipts)} of your receipts. Ask me anything!")
        
        # Quick questions
        st.markdown("### 🎯 Quick Questions")
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📊 Summarize my receipts", use_container_width=True):
                st.session_state.quick_question = "Give me a summary of all my receipts"
            if st.button("💰 What's my total spending?", use_container_width=True):
                st.session_state.quick_question = "What's my total spending across all receipts?"
        
        with col2:
            if st.button("🏪 Most expensive purchase?", use_container_width=True):
                st.session_state.quick_question = "What was my most expensive purchase?"
            if st.button("📅 Recent receipts", use_container_width=True):
                st.session_state.quick_question = "Show me my most recent receipts"
        
        st.divider()
        
        # Chat history
        st.markdown("### 💬 Conversation")
        
        chat_container = st.container()
        with chat_container:
            if not st.session_state.chat_history:
                st.info("👋 Start a conversation! Ask me about your receipts.")
            else:
                for msg in st.session_state.chat_history:
                    if msg['role'] == 'user':
                        st.markdown(f'<div class="user-msg">🧑 {msg["content"]}</div>', 
                                  unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="ai-msg">🤖 {msg["content"]}</div>', 
                                  unsafe_allow_html=True)
        
        # Chat input
        st.divider()
        
        # Handle quick question
        if 'quick_question' in st.session_state:
            user_input = st.session_state.quick_question
            del st.session_state.quick_question
            
            # Process immediately
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            with st.spinner("🤔 Thinking..."):
                response = gemini_service.chat(user_input, receipts)
            
            st.session_state.chat_history.append({
                'role': 'assistant',
                'content': response
            })
            
            st.rerun()
        
        # Text input
        with st.form("chat_form", clear_on_submit=True):
            user_input = st.text_input(
                "Ask me anything about your receipts...",
                placeholder="e.g., What's my total spending?",
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns([6, 1])
            with col1:
                submit = st.form_submit_button("Send 💬", use_container_width=True)
            with col2:
                clear = st.form_submit_button("Clear 🗑️", use_container_width=True)
            
            if clear:
                st.session_state.chat_history = []
                st.rerun()
            
            if submit and user_input.strip():
                # Add user message
                st.session_state.chat_history.append({
                    'role': 'user',
                    'content': user_input
                })
                
                # Get AI response
                with st.spinner("🤔 Thinking..."):
                    response = gemini_service.chat(user_input, receipts)
                
                # Add AI response
                st.session_state.chat_history.append({
                    'role': 'assistant',
                    'content': response
                })
                
                st.rerun()

# ============================================================================
# FOOTER
# ============================================================================
st.sidebar.divider()
st.sidebar.caption("PocketPilot AI")
st.sidebar.caption("Powered by Google AI")
