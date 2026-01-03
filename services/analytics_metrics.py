# services/analytics_metrics.py

import pandas as pd
from typing import Dict

def compute_basic_metrics(df: pd.DataFrame) -> Dict:
    """
    Compute total income, total expenses, and net balance.
    """
    if df.empty:
        return {
            "total_income": 0.0,
            "total_expenses": 0.0,
            "net_balance": 0.0,
        }

    income = df[df["type"] == "income"]["amount"].sum()
    expenses = df[df["type"] == "expense"]["amount"].sum()

    return {
        "total_income": float(income),
        "total_expenses": float(expenses),
        "net_balance": float(income - expenses),
    }


def compute_category_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute total expense amount per category.
    Returns a DataFrame sorted by amount descending.
    """
    if df.empty:
        return pd.DataFrame(columns=["category", "amount"])

    expenses_df = df[df["type"] == "expense"]

    if expenses_df.empty:
        return pd.DataFrame(columns=["category", "amount"])

    category_totals = (
        expenses_df
        .groupby("category", as_index=False)["amount"]
        .sum()
        .sort_values(by="amount", ascending=False)
    )

    return category_totals


def compute_monthly_totals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute monthly expense totals.
    """
    if df.empty:
        return pd.DataFrame(columns=["month", "amount"])

    expenses_df = df[df["type"] == "expense"].copy()

    if expenses_df.empty:
        return pd.DataFrame(columns=["month", "amount"])

    expenses_df["month"] = expenses_df["date"].dt.to_period("M").astype(str)

    monthly_totals = (
        expenses_df
        .groupby("month", as_index=False)["amount"]
        .sum()
        .sort_values(by="month")
    )

    return monthly_totals


def compute_month_over_month_change(monthly_df: pd.DataFrame) -> float:
    """
    Compute percentage change between last two months.
    Returns 0.0 if insufficient data.
    """
    if monthly_df.shape[0] < 2:
        return 0.0

    last = monthly_df.iloc[-1]["amount"]
    previous = monthly_df.iloc[-2]["amount"]

    if previous == 0:
        return 0.0

    return round(((last - previous) / previous) * 100, 2)
