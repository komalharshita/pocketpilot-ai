"""
Dashboard UI component
Displays receipt data in a clean, readable table format
"""

import gradio as gr
from services.firebase_manager import FirebaseManager
from utils.helpers import (
    format_receipts_for_display,
    calculate_spending_summary,
    format_currency
)

def create_dashboard_tab(firebase_manager: FirebaseManager):
    """
    Create dashboard UI components (NO Tabs, NO lifecycle)
    """

    def load_dashboard():
        try:
            receipts = firebase_manager.get_all_receipts()

            if not receipts:
                return (
                    [],
                    "No receipts found. Upload your first receipt to get started!",
                    "Total: $0.00 | Receipts: 0 | Average: $0.00"
                )

            table_data = format_receipts_for_display(receipts)
            summary = calculate_spending_summary(receipts)

            summary_text = (
                f"Total Spent: {format_currency(summary['total_spent'])} | "
                f"Receipts: {summary['total_receipts']} | "
                f"Average: {format_currency(summary['average_transaction'])}"
            )

            status_msg = f"✅ Loaded {len(receipts)} receipt(s) successfully"

            return table_data, status_msg, summary_text

        except Exception as e:
            return (
                [],
                f"❌ Error loading receipts: {str(e)}",
                "Total: $0.00 | Receipts: 0 | Average: $0.00"
            )

    # UI ONLY
    gr.Markdown("# 📊 Dashboard")
    gr.Markdown("View all your receipts and spending summary")

    summary_display = gr.Markdown(
        "Total: $0.00 | Receipts: 0 | Average: $0.00"
    )

    refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary")

    status_msg = gr.Markdown("Click refresh to load receipts")

    receipts_table = gr.Dataframe(
        headers=["Date", "Merchant", "Amount", "Category", "ID"],
        datatype=["str", "str", "str", "str", "str"],
        column_count=5,   # ✅ Gradio 6.x
        interactive=False,
        wrap=True,
        label="Your Receipts"
    )

    refresh_btn.click(
        fn=load_dashboard,
        outputs=[receipts_table, status_msg, summary_display]
    )

    # RETURN handles so Blocks can attach lifecycle
    return load_dashboard, receipts_table, status_msg, summary_display
