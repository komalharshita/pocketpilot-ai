"""
Dashboard UI component (fixed + stable)
- INR currency (₹)
- Exactly 10 receipts shown
- Short IDs
- Dates span Jan 2024 → Dec 2025
- Blue logo color theme
- NO component type leaks (Gradio-safe)
"""

import gradio as gr
import pandas as pd
from services.firebase_manager import FirebaseManager

# ===== Brand Colors (from logo) =====
ACCENT_COLOR = "#1ec9ff"
SECONDARY_COLOR = "#2a7cff"

# ===== Demo receipts (used only to fill up to 10) =====
DEMO_RECEIPTS = [
    {"Date": "2024-01-15", "Merchant": "Zomato", "Amount": 412.50, "Category": "Dining", "ID": "5767ERT"},
    {"Date": "2024-03-02", "Merchant": "Amazon", "Amount": 2250.00, "Category": "Shopping", "ID": "A12B3CD"},
    {"Date": "2024-06-18", "Merchant": "Starbucks", "Amount": 342.75, "Category": "Dining", "ID": "B78C9DE"},
    {"Date": "2024-09-10", "Merchant": "Walmart", "Amount": 1580.00, "Category": "Groceries", "ID": "C90D1EF"},
    {"Date": "2024-12-25", "Merchant": "Uber Eats", "Amount": 425.30, "Category": "Dining", "ID": "D23E4FG"},
    {"Date": "2025-02-11", "Merchant": "Flipkart", "Amount": 3200.00, "Category": "Shopping", "ID": "E45F6GH"},
    {"Date": "2025-05-05", "Merchant": "Big Bazaar", "Amount": 1890.50, "Category": "Groceries", "ID": "F67G8HI"},
    {"Date": "2025-08-21", "Merchant": "Zomato", "Amount": 410.00, "Category": "Dining", "ID": "G89H0IJ"},
    {"Date": "2025-10-03", "Merchant": "Amazon", "Amount": 1299.99, "Category": "Shopping", "ID": "H01I2JK"},
    {"Date": "2025-12-10", "Merchant": "Metro Mart", "Amount": 1120.00, "Category": "Groceries", "ID": "I23J4KL"},
]


def format_inr(x: float) -> str:
    return f"₹{x:,.2f}"


def create_dashboard_tab(firebase_manager: FirebaseManager):
    """
    RETURNS (order matters — matches main.py):
    load_dashboard,
    receipts_table,
    status_message,
    summary_display,
    category_chart,
    time_chart,
    merchant_chart
    """

    # ===== UI COMPONENTS (REAL INSTANCES) =====
    gr.Markdown("## 📊 Dashboard")

    status_message = gr.Markdown("")
    summary_display = gr.Markdown("")

    receipts_table = gr.Dataframe(
        headers=["Date", "Merchant", "Amount", "Category", "ID"],
        interactive=False,
        wrap=True,
        label="Receipts"
    )

    gr.Markdown("## 📈 Spending Insights")

    with gr.Row():
        category_chart = gr.BarPlot(
            label="Spending by Category",
            x="label",
            y="value",
            color=ACCENT_COLOR
        )

        time_chart = gr.LinePlot(
            label="Spending Over Time",
            x="label",
            y="value",
            color=SECONDARY_COLOR
        )

    merchant_chart = gr.BarPlot(
        label="Spending by Merchant",
        x="label",
        y="value",
        color=ACCENT_COLOR
    )

    # ===== DATA LOADER =====
    def load_dashboard():
        raw = firebase_manager.get_all_receipts() or []
        records = []

        for r in raw:
            try:
                amt = float(r.get("total_amount", r.get("amount", 0)))
                if amt <= 0:
                    continue

                records.append({
                    "Date": r.get("transaction_date", r.get("date", "Unknown")),
                    "Merchant": r.get("merchant_name", r.get("merchant", "Unknown")),
                    "Amount": amt,
                    "Category": r.get("category", "Other"),
                    "ID": str(r.get("id", ""))[:7]
                })
            except Exception:
                continue

        # Fill up to exactly 10
        for demo in DEMO_RECEIPTS:
            if len(records) >= 10:
                break
            records.append(demo)

        # Sort by date (desc) and cap at 10
        df = pd.DataFrame(records)
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
        df = df.sort_values("Date", ascending=False).head(10)

        total = df["Amount"].sum()
        avg = df["Amount"].mean()

        summary_text = f"Total Spent: {format_inr(total)} | Receipts: 10 | Average: {format_inr(avg)}"
        status_text = "✅ Showing latest 10 receipts"

        # Table rows (formatted)
        table_rows = [
            [str(r.Date.date()), r.Merchant, format_inr(r.Amount), r.Category, r.ID]
            for r in df.itertuples()
        ]

        by_category = df.groupby("Category", as_index=False)["Amount"].sum().rename(columns={"Category": "label", "Amount": "value"})
        by_date = df.groupby(df["Date"].dt.date, as_index=False)["Amount"].sum().rename(columns={"Date": "label", "Amount": "value"})
        by_merchant = df.groupby("Merchant", as_index=False)["Amount"].sum().rename(columns={"Merchant": "label", "Amount": "value"})

        return (
            table_rows,
            status_text,
            summary_text,
            by_category,
            by_date,
            by_merchant
        )

    # ✅ RETURN REAL COMPONENT INSTANCES ONLY
    return (
        load_dashboard,
        receipts_table,
        status_message,
        summary_display,
        category_chart,
        time_chart,
        merchant_chart
    )
