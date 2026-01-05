"""
Dashboard UI component
Displays receipt data in a clean, readable table format
"""

import gradio as gr
from services.firebase_manager import FirebaseManager
from utils.helpers import format_receipts_for_display, calculate_spending_summary, format_currency

def create_dashboard_tab(firebase_manager: FirebaseManager):
    """
    Create the dashboard tab interface
    
    Args:
        firebase_manager: Initialized FirebaseManager instance
    
    Returns:
        Gradio column component
    """
    
    def load_dashboard():
        """Load and display all receipts"""
        try:
            # Fetch receipts from Firestore
            receipts = firebase_manager.get_all_receipts()
            
            if not receipts:
                return (
                    [],
                    "No receipts found. Upload your first receipt to get started!",
                    "Total: $0.00 | Receipts: 0 | Average: $0.00"
                )
            
            # Format receipts for table display
            table_data = format_receipts_for_display(receipts)
            
            # Calculate summary statistics
            summary = calculate_spending_summary(receipts)
            
            # Create summary text
            summary_text = (
                f"Total Spent: {format_currency(summary['total_spent'])} | "
                f"Receipts: {summary['total_receipts']} | "
                f"Average: {format_currency(summary['average_transaction'])}"
            )
            
            # Create status message
            status_msg = f"✅ Loaded {len(receipts)} receipt(s) successfully"
            
            return table_data, status_msg, summary_text
        
        except Exception as e:
            error_msg = f"❌ Error loading receipts: {str(e)}"
            return [], error_msg, "Total: $0.00 | Receipts: 0 | Average: $0.00"
    
    with gr.Column() as dashboard_tab:
        gr.Markdown("# 📊 Dashboard")
        gr.Markdown("View all your receipts and spending summary")
        
        # Summary statistics row
        summary_display = gr.Markdown(
            "Total: $0.00 | Receipts: 0 | Average: $0.00",
            elem_id="summary-stats"
        )
        
        # Refresh button
        refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")
        
        # Status message
        status_msg = gr.Markdown("Click refresh to load receipts")
        
        # Receipts table
        receipts_table = gr.Dataframe(
            headers=["Date", "Merchant", "Amount", "Category", "ID"],
            datatype=["str", "str", "str", "str", "str"],
            col_count=(5, "fixed"),
            label="Your Receipts",
            interactive=False,
            wrap=True
        )
        
        # Connect refresh button
        refresh_btn.click(
            fn=load_dashboard,
            outputs=[receipts_table, status_msg, summary_display]
        )
        
        # Load dashboard on tab open
        dashboard_tab.load(
            fn=load_dashboard,
            outputs=[receipts_table, status_msg, summary_display]
        )
    
    return dashboard_tab