import plotly.express as px
import pandas as pd


def monthly_expense_chart(df):
    # ✅ Always return a valid Plotly figure
    if df is None or df.empty:
        return px.bar(title="No expense data available")

    # ✅ Safe date conversion (prevents crashes)
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    # Remove rows with invalid dates
    df = df.dropna(subset=["date"])

    # Filter only expenses
    expenses = df[df["type"] == "expense"]

    if expenses.empty:
        return px.bar(title="No expense data available")

    # Group by month
    monthly = (
        expenses
        .groupby(expenses["date"].dt.to_period("M"))["amount"]
        .sum()
        .reset_index()
    )

    monthly["date"] = monthly["date"].astype(str)

    fig = px.bar(
        monthly,
        x="date",
        y="amount",
        title="Monthly Expenses",
        labels={
            "date": "Month",
            "amount": "Amount Spent"
        }
    )

    return fig


def category_expense_chart(df):
    # ✅ Always return a valid Plotly figure
    if df is None or df.empty:
        return px.pie(title="No expense data available")

    # Filter only expenses
    expenses = df[df["type"] == "expense"]

    if expenses.empty:
        return px.pie(title="No expense data available")

    category = (
        expenses
        .groupby("category")["amount"]
        .sum()
        .reset_index()
    )

    fig = px.pie(
        category,
        names="category",
        values="amount",
        title="Spending by Category"
    )

    return fig
