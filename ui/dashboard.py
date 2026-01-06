"""
Dashboard UI component
Displays receipt data and spending summary
"""

import gradio as gr
import pandas as pd
from services.firebase_manager import FirebaseManager
from utils.helpers import (
    format_receipts_for_display,
    calculate_spending_summary,
    format_currency
)

# ------------------ SAMPLE DATA (UI DEMO ONLY) ------------------
DEMO_RECEIPTS = [
    {
        "date": "2025-01-01",
        "merchant": "Zomato",
        "amount": 119.28,
        "category": "Food",
        "id": "demo_001"
    },
    {
        "date": "2025-01-03",
        "merchant": "Amazon",
        "amount": 45.99,
        "category": "Shopping",
        "id": "demo_002"
    },
    {
        "date": "2025-01-05",
        "merchant": "Uber",
        "amount": 18.50,
        "category": "Transport",
        "id": "demo_003"
    }
]


def normalize_receipts(receipts: list) -> list:
    """
    Normalize Firebase receipts into a strict, chart-safe format.
    Invalid or empty records are ignored.
    """
    clean = []

    for r in receipts:
        try:
            amount = float(r.get("amount", 0))
            if amount <= 0:
                continue  # ❗ skip zero / invalid receipts

            clean.append({
                "date": r.get("date", "2025-01-01"),
                "merchant": r.get("merchant", "Unknown"),
                "amount": amount,
                "category": r.get("category", "Other"),
                "id": r.get("id", "N/A")
            })
        except Exception:
            continue

    return clean


def create_dashboard_tab(firebase_manager: FirebaseManager):

    def load_dashboard():
        try:
            raw_receipts = firebase_manager.get_all_receipts()
            receipts = normalize_receipts(raw_receipts)

            # 🔹 Use demo data if real data is empty or unusable
            if not receipts:
                receipts = DEMO_RECEIPTS
                status_text = "🧪 Showing sample data (upload receipts to replace)"
            else:
                status_text = f"✅ Loaded {len(receipts)} receipt(s)"

            # ---------- Table ----------
            table_data = format_receipts_for_display(receipts)

            # ---------- Summary ----------
            summary = calculate_spending_summary(receipts)
            summary_text = (
                f"Total Spent: {format_currency(summary['total_spent'])} | "
                f"Receipts: {summary['total_receipts']} | "
                f"Average: {format_currency(summary['average_transaction'])}"
            )

            # ---------- Charts ----------
            df = pd.DataFrame(receipts)

            category_chart = (
                df.groupby("category", as_index=False)["amount"]
                .sum()
                .rename(columns={"category": "label", "amount": "value"})
            )

            time_chart = (
                df.groupby("date", as_index=False)["amount"]
                .sum()
                .rename(columns={"date": "label", "amount": "value"})
            )

            merchant_chart = (
                df.groupby("merchant", as_index=False)["amount"]
                .sum()
                .sort_values("amount", ascending=False)
                .head(5)
                .rename(columns={"merchant": "label", "amount": "value"})
            )

            return (
                table_data,
                status_text,
                summary_text,
                category_chart,
                time_chart,
                merchant_chart
            )

        except Exception as e:
            empty = pd.DataFrame(columns=["label", "value"])
            return [], f"❌ Error loading dashboard: {e}", "", empty, empty, empty

    # ================= UI =================

    gr.Markdown("# 📊 Dashboard")
    gr.Markdown("View your receipts and spending summary")

    summary_display = gr.Markdown("Total: $0.00 | Receipts: 0 | Average: $0.00")

    refresh_button = gr.Button("🔄 Refresh Dashboard", variant="primary")
    status_message = gr.Markdown("Click refresh to load receipts")

    receipts_table = gr.Dataframe(
        headers=["Date", "Merchant", "Amount", "Category", "ID"],
        datatype=["str", "str", "str", "str", "str"],
        interactive=False,
        label="Your Receipts"
    )

    gr.Markdown("## 📈 Spending Insights")

    with gr.Row():
        category_chart = gr.BarPlot(
            label="Spending by Category",
            x="label",
            y="value"
        )

        merchant_chart = gr.BarPlot(
            label="Top Merchants",
            x="label",
            y="value"
        )

    time_chart = gr.LinePlot(
        label="Spending Over Time",
        x="label",
        y="value"
    )

    refresh_button.click(
        fn=load_dashboard,
        outputs=[
            receipts_table,
            status_message,
            summary_display,
            category_chart,
            time_chart,
            merchant_chart
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
