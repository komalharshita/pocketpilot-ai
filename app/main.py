"""
PocketPilot AI - Main Application
A simple personal finance app with receipt parsing and AI chatbot

Features:
1. Dashboard - View all receipts
2. Receipt Upload - Process receipts with Google Document AI
3. AI Chatbot - Financial assistant powered by Google Gemini
"""

import gradio as gr
from config.settings import Settings
from services.firebase_manager import FirebaseManager
from services.document_ai_processor import DocumentAIProcessor
from services.gemini_manager import GeminiManager
from ui.dashboard import create_dashboard_tab
from ui.receipt_upload import create_receipt_upload_tab
from ui.chatbot import create_chatbot_tab

# Custom CSS for better UI
CUSTOM_CSS = """
#summary-stats {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 20px;
}

.gradio-container {
    max-width: 1200px !important;
}

footer {
    display: none !important;
}
"""

def create_app():
    """
    Create and configure the Gradio application
    
    Returns:
        Gradio Blocks interface
    """
    
    print("="*60)
    print("🚀 Initializing PocketPilot AI...")
    print("="*60)
    
    try:
        # Initialize services
        print("\n📦 Initializing services...")
        firebase_manager = FirebaseManager()
        doc_ai_processor = DocumentAIProcessor()
        gemini_manager = GeminiManager()
        
        print("\n✅ All services initialized successfully!")
        print("="*60)
    
    except Exception as e:
        print(f"\n❌ Initialization failed: {e}")
        print("="*60)
        raise
    
    # Create Gradio interface
    with gr.Blocks(
        title="PocketPilot AI - Personal Finance Assistant",
        theme=gr.themes.Soft(
            primary_hue="purple",
            secondary_hue="blue",
            neutral_hue="slate",
        ),
        css=CUSTOM_CSS
    ) as app:
        
        # Header
        gr.Markdown(
            """
            # 🚀 PocketPilot AI
            ### Your Personal Finance Assistant
            
            Upload receipts, track spending, and get AI-powered financial insights
            """
        )
        
        # Create tabs
        with gr.Tabs() as tabs:
            with gr.Tab("📊 Dashboard", id="dashboard"):
                create_dashboard_tab(firebase_manager)
            
            with gr.Tab("📤 Upload Receipt", id="upload"):
                create_receipt_upload_tab(firebase_manager, doc_ai_processor)
            
            with gr.Tab("💬 Financial Assistant", id="chatbot"):
                create_chatbot_tab(gemini_manager, firebase_manager)
        
        # Footer
        gr.Markdown(
            """
            ---
            **PocketPilot AI** | Powered by Google Document AI & Gemini | Built with Gradio
            
            ⚠️ **Privacy Note**: This is a demo application. Always review and verify financial data.
            """
        )
    
    return app

def main():
    """Main entry point"""
    try:
        # Create app
        app = create_app()
        
        # Launch app
        print("\n" + "="*60)
        print("🌐 Launching Gradio application...")
        print(f"📍 Host: {Settings.APP_HOST}")
        print(f"🔌 Port: {Settings.APP_PORT}")
        print("="*60 + "\n")
        
        app.launch(
            server_name=Settings.APP_HOST,
            server_port=Settings.APP_PORT,
            share=False,  # Set to True if you want a public URL
            show_error=True,
            quiet=False
        )
    
    except Exception as e:
        print(f"\n❌ Application failed to start: {e}")
        raise

if __name__ == "__main__":
    main()