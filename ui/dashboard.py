"""
Dashboard UI component
Displays receipt data and spending summary with charts
"""

import gradio as gr
import pandas as pd
from services.firebase_manager import FirebaseManager
from utils.helpers import (
    format_receipts_for_display,
    calculate_spending_summary,
    format_currency,
    generate_short_id
)
from datetime import datetime, timedelta
import random

DEMO_RECEIPTS = [
    {"date": "2024-01-15", "merchant": "Swiggy", "amount": 245.50, "category": "Food & Dining"},
    {"date": "2024-02-20", "merchant": "Amazon India", "amount": 1299.00, "category": "Shopping"},
    {"date": "2024-03-10", "merchant": "Big Bazaar", "amount": 2150.75, "category": "Groceries"},
    {"date": "2024-04-05", "merchant": "Ola Cabs", "amount": 180.00, "category": "Transport"},
    {"date": "2024-05-18", "merchant": "Reliance Digital", "amount": 4599.00, "category": "Electronics"},
    {"date": "2024-06-22", "merchant": "Zomato", "amount": 385.50, "category": "Food & Dining"},
    {"date": "2024-07-30", "merchant": "Apollo Pharmacy", "amount": 450.00, "category": "Healthcare"},
    {"date": "2024-08-14", "merchant": "BookMyShow", "amount": 600.00, "category": "Entertainment"},
    {"date": "2024-09-25", "merchant": "DMart", "amount": 1850.25, "category": "Groceries"},
    {"date": "2024-10-12", "merchant": "Uber", "amount": 220.00, "category": "Transport"},
    {"date": "2024-11-08", "merchant": "Flipkart", "amount": 899.00, "category": "Shopping"},
    {"date": "2024-12-20", "merchant": "Dominos", "amount": 549.00, "category": "Food & Dining"},
    {"date": "2025-01-05", "merchant": "Myntra", "amount": 1599.00, "category": "Fashion"},
    {"date": "2025-02-14", "merchant": "Starbucks", "amount": 425.00, "category": "Food & Dining"},
    {"date": "2025-03-22", "merchant": "PVR Cinemas", "amount": 800.00, "category": "Entertainment"},
]


def normalize_receipts(raw_receipts: list) -> list:
    """Convert Firebase receipts to standardized format"""
    normalized = []
    
    for r in raw_receipts:
        try:
            amount = float(r.get("total_amount", 0))
            if amount <= 0:
                continue
            
            full_id = r.get("id", "")
            short_id = generate_short_id(full_id) if full_id else "DEMO"
            
            normalized.append({
                "date": r.get("transaction_date", "2025-01-01"),
                "merchant": r.get("merchant_name", "Unknown"),
                "amount": amount,
                "category": r.get("category", "Other"),
                "id": short_id
            })
        except Exception:
            continue
    
    return normalized


def ensure_ten_receipts(real_receipts: list) -> list:
    """Ensure exactly 10 receipts by filling with demo data if needed"""
    if len(real_receipts) >= 10:
        return sorted(real_receipts, key=lambda x: x['date'], reverse=True)[:10]
    
    needed = 10 - len(real_receipts)
    demo_sample = random.sample(DEMO_RECEIPTS, min(needed, len(DEMO_RECEIPTS)))
    
    for demo in demo_sample:
        demo['id'] = generate_short_id(demo['merchant'] + demo['date'])
    
    combined = real_receipts + demo_sample
    return sorted(combined, key=lambda x: x['date'], reverse=True)[:10]


def create_dashboard_tab(firebase_manager: FirebaseManager):
    
    dashboard_state = gr.State(value=0)
    
    def load_dashboard(refresh_trigger=0):
        try:
            raw_receipts = firebase_manager.get_all_receipts()
            normalized = normalize_receipts(raw_receipts)
            receipts = ensure_ten_receipts(normalized)
            
            if len(normalized) == 0:
                status_text = "🧪 Showing demo data (upload receipts to replace)"
            else:
                status_text = f"✅ Loaded {len(normalized)} receipt(s)"
            
            table_data = format_receipts_for_display(receipts)
            
            summary = calculate_spending_summary(receipts)
            summary_text = (
                f"**Total Spent:** {format_currency(summary['total_spent'])} | "
                f"**Receipts:** {summary['total_receipts']} | "
                f"**Average:** {format_currency(summary['average_transaction'])}"
            )
            
            df = pd.DataFrame(receipts)
            
            category_data = (
                df.groupby("category", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )
            
            time_data = (
                df.groupby("date", as_index=False)["amount"]
                .sum()
                .sort_values("date")
            )
            
            merchant_data = (
                df.groupby("merchant", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
                .head(5)
            )
            
            return (
                table_data,
                status_text,
                summary_text,
                category_data,
                time_data,
                merchant_data,
                refresh_trigger
            )
            
        except Exception as e:
            empty_df = pd.DataFrame(columns=["category", "amount"])
            return (
                [],
                f"❌ Error: {e}",
                "Total: ₹0.00 | Receipts: 0 | Average: ₹0.00",
                empty_df,
                empty_df,
                empty_df,
                refresh_trigger
            )
    
    gr.Markdown("# 📊 Dashboard")
    gr.Markdown("*View your receipts and spending insights*")
    
    summary_display = gr.Markdown("**Total:** ₹0.00 | **Receipts:** 0 | **Average:** ₹0.00")
    
    refresh_button = gr.Button("🔄 Refresh Dashboard", variant="primary")
    status_message = gr.Markdown("Click refresh to load receipts")
    
    receipts_table = gr.Dataframe(
        headers=["Date", "Merchant", "Amount", "Category", "ID"],
        datatype=["str", "str", "str", "str", "str"],
        interactive=False,
        label="Recent Transactions (Last 10)"
    )
    
    gr.Markdown("## 📈 Spending Insights")
    
    with gr.Row():
        category_chart = gr.BarPlot(
            x="category",
            y="amount",
            title="Spending by Category",
            x_title="Category",
            y_title="Amount (₹)",
            color="#1ec9ff"
        )
        
        merchant_chart = gr.BarPlot(
            x="merchant",
            y="amount",
            title="Top 5 Merchants",
            x_title="Merchant",
            y_title="Amount (₹)",
            color="#2a7cff"
        )
    
    time_chart = gr.LinePlot(
        x="date",
        y="amount",
        title="Spending Over Time",
        x_title="Date",
        y_title="Amount (₹)",
        color="#1ec9ff"
    )
    
    refresh_button.click(
        fn=load_dashboard,
        inputs=[dashboard_state],
        outputs=[
            receipts_table,
            status_message,
            summary_display,
            category_chart,
            time_chart,
            merchant_chart,
            dashboard_state
        ]
    )
    
    return (
        load_dashboard,
        receipts_table,
        status_message,
        summary_display,
        category_chart,
        time_chart,
        merchant_chart
    )