# app/dashboard.py

import streamlit as st
from services.analytics_data import get_transactions_df
from services.analytics_metrics import (
    compute_basic_metrics,
    compute_category_totals,
    compute_monthly_totals,
    compute_month_over_month_change,
)
from app.transaction_list import transaction_list


def dashboard_page(user):
    user_id = user["localId"]

    st.subheader("Dashboard")

    # Fetch data
    df = get_transactions_df(user_id)

    # -----------------------------
    # Summary Metrics
    # -----------------------------
    metrics = compute_basic_metrics(df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{metrics['total_income']:.2f}")
    col2.metric("Total Expenses", f"₹{metrics['total_expenses']:.2f}")
    col3.metric("Net Balance", f"₹{metrics['net_balance']:.2f}")

    # -----------------------------
    # Category Breakdown
    # -----------------------------
    st.divider()
    st.subheader("Spending by Category")

    category_df = compute_category_totals(df)

    if category_df.empty:
        st.info("No expense data available.")
    else:
        st.dataframe(category_df, use_container_width=True)

    # -----------------------------
    # Monthly Trend
    # -----------------------------
    st.divider()
    st.subheader("Monthly Expense Trend")

    monthly_df = compute_monthly_totals(df)

    if monthly_df.empty:
        st.info("Not enough data for monthly trends.")
    else:
        st.line_chart(monthly_df.set_index("month")["amount"])

        mom_change = compute_month_over_month_change(monthly_df)
        st.caption(f"Month-over-month change: {mom_change}%")

    # -----------------------------
    # Transaction List
    # -----------------------------
    st.divider()
    transaction_list(user)
