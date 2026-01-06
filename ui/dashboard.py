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
from datetime import datetime


def normalize_receipts(raw_receipts: list) -> list:
    """
    Convert Firebase receipts to standardized format
    IMPORTANT FIX:
    - Use created_at for date (not static transaction_date)
    - Remove all demo / filler logic
    """
    normalized = []

    for r in raw_receipts:
        try:
            amount = float(r.get("total_amount", 0))
            if amount <= 0:
                continue

            full_id = r.get("id", "")
            short_id = generate_short_id(full_id) if full_id else ""

            # created_at comes as string "YYYY-MM-DD HH:MM:SS"
            created_at = r.get("created_at")
            if created_at:
                date_val = created_at.split(" ")[0]
            else:
                date_val = datetime.now().strftime("%Y-%m-%d")

            normalized.append({
                "date": date_val,
                "merchant": r.get("merchant_name", ""),
                "amount": amount,
                "category": r.get("category", ""),
                "id": short_id
            })
        except Exception:
            continue

    return normalized


def create_dashboard_tab(firebase_manager: FirebaseManager):

    def load_dashboard():
        try:
            raw_receipts = firebase_manager.get_all_receipts()
            receipts = normalize_receipts(raw_receipts)

            if not receipts:
                empty_df = pd.DataFrame(columns=["category", "amount"])
                return (
                    [],
                    "No receipts uploaded yet.",
                    "**Total:** ₹0.00 | **Receipts:** 0 | **Average:** ₹0.00",
                    empty_df,
                    empty_df,
                    empty_df
                )

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

            merchant_data = (
                df.groupby("merchant", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
            )

            time_data = (
                df.groupby("date", as_index=False)["amount"]
                .sum()
                .sort_values("date")
            )

            return (
                table_data,
                f"✅ Loaded {len(receipts)} receipt(s)",
                summary_text,
                category_data,
                merchant_data,
                time_data
            )

        except Exception as e:
            empty_df = pd.DataFrame(columns=["category", "amount"])
            return (
                [],
                f"❌ Error: {e}",
                "**Total:** ₹0.00 | **Receipts:** 0 | **Average:** ₹0.00",
                empty_df,
                empty_df,
                empty_df
            )

    gr.Markdown("# DASHBOARD")
    gr.Markdown("*View your receipts and spending insights*")

    summary_display = gr.Markdown("**Total:** ₹0.00 | **Receipts:** 0 | **Average:** ₹0.00")
    status_message = gr.Markdown("")

    receipts_table = gr.Dataframe(
        headers=["Date", "Merchant", "Amount", "Category", "ID"],
        datatype=["str", "str", "str", "str", "str"],
        interactive=False,
        label="Transactions"
    )

    gr.Markdown("## INSIGHTS")

    with gr.Row():
        category_chart = gr.BarPlot(
            x="category",
            y="amount",
            color="category",              
            color_map={
                "Dining": "#1ec9ff",
                "Groceries": "#2a7cff",
                "Shopping": "#7c7cff",
                "Transportation": "#00c2a8",
                "Other": "#8892b0"
            },
            title="Spending by Category",
            x_title="Category",
            y_title="Amount (₹)"
        )

        merchant_chart = gr.BarPlot(
            x="merchant",
            y="amount",
            color="merchant",              
            color_map={
                "Amazon": "#1ec9ff",
                "Starbucks": "#2a7cff",
                "Zomato": "#6b6eff",
                "Uber": "#9e00c2",
                "Walmart": "#f357fe"
            },
            title="Spending by Merchant",
            x_title="Merchant",
            y_title="Amount (₹)"
        )

    time_chart = gr.LinePlot(
        x="date",
        y="amount",
        title="Spending Over Time",
        x_title="Date",
        y_title="Amount (₹)",
        color="#1ec9ff"
    )

    return (
        load_dashboard,
        receipts_table,
        status_message,
        summary_display,
        category_chart,
        merchant_chart,
        time_chart
    )
