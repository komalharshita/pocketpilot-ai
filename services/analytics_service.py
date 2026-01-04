"""
Analytics Service for PocketPilot AI
Simple financial analytics built on pandas
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional


class FinancialAnalytics:
    """
    Lightweight analytics engine for transaction data
    """

    def __init__(self, transactions_df: pd.DataFrame):
        self.df = transactions_df.copy()

        if not self.df.empty:
            self.df["date"] = pd.to_datetime(self.df["date"], errors="coerce")
            self.df = self.df.dropna(subset=["date"])

    # ------------------------------------------------------------------
    # Core summaries
    # ------------------------------------------------------------------

    def get_summary(self, period: Optional[str] = None) -> Dict:
        df = self._filter_by_period(period)

        if df.empty:
            return {
                "income": 0.0,
                "expenses": 0.0,
                "balance": 0.0,
                "transactions": 0,
                "savings_rate": 0.0
            }

        income = df[df["type"] == "Income"]["amount"].sum()
        expenses = df[df["type"] == "Expense"]["amount"].sum()
        balance = income - expenses
        savings_rate = (balance / income * 100) if income > 0 else 0.0

        return {
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "balance": round(balance, 2),
            "transactions": len(df),
            "savings_rate": round(savings_rate, 2)
        }

    # ------------------------------------------------------------------
    # Category analysis
    # ------------------------------------------------------------------

    def category_breakdown(self, period: Optional[str] = None) -> pd.Series:
        df = self._filter_by_period(period)
        expenses = df[df["type"] == "Expense"]

        if expenses.empty:
            return pd.Series(dtype=float)

        return expenses.groupby("category")["amount"].sum().sort_values(ascending=False)

    # ------------------------------------------------------------------
    # Time-based insights
    # ------------------------------------------------------------------

    def daily_expenses(self, period: Optional[str] = None) -> pd.DataFrame:
        df = self._filter_by_period(period)
        expenses = df[df["type"] == "Expense"]

        if expenses.empty:
            return pd.DataFrame(columns=["date", "amount"])

        daily = (
            expenses
            .groupby(expenses["date"].dt.date)["amount"]
            .sum()
            .reset_index()
        )

        daily.columns = ["date", "amount"]
        return daily

    # ------------------------------------------------------------------
    # Simple trend comparison
    # ------------------------------------------------------------------

    def spending_trend(self) -> Dict:
        today = datetime.now()
        last_30 = self.df[self.df["date"] >= today - timedelta(days=30)]
        prev_30 = self.df[
            (self.df["date"] < today - timedelta(days=30)) &
            (self.df["date"] >= today - timedelta(days=60))
        ]

        current = last_30[last_30["type"] == "Expense"]["amount"].sum()
        previous = prev_30[prev_30["type"] == "Expense"]["amount"].sum()

        if previous > 0:
            change = ((current - previous) / previous) * 100
        else:
            change = 0.0

        trend = "increasing" if change > 5 else "decreasing" if change < -5 else "stable"

        return {
            "current": round(current, 2),
            "previous": round(previous, 2),
            "change_pct": round(change, 2),
            "trend": trend
        }

    # ------------------------------------------------------------------
    # Forecast (very simple)
    # ------------------------------------------------------------------

    def forecast_monthly_expense(self) -> Dict:
        expenses = self.df[self.df["type"] == "Expense"]

        if expenses.empty:
            return {"forecast": 0.0, "confidence": "low"}

        this_month = expenses[
            (expenses["date"].dt.month == datetime.now().month) &
            (expenses["date"].dt.year == datetime.now().year)
        ]

        if this_month.empty:
            avg = expenses.groupby(
                [expenses["date"].dt.year, expenses["date"].dt.month]
            )["amount"].sum().mean()

            return {
                "forecast": round(avg, 2),
                "confidence": "medium",
                "method": "historical_average"
            }

        days_passed = datetime.now().day
        total = this_month["amount"].sum()
        daily_avg = total / max(days_passed, 1)
        days_in_month = datetime.now().replace(day=28).day

        return {
            "forecast": round(daily_avg * days_in_month, 2),
            "spent_so_far": round(total, 2),
            "confidence": "high",
            "method": "current_month_projection"
        }

    # ------------------------------------------------------------------
    # Internal helper
    # ------------------------------------------------------------------

    def _filter_by_period(self, period: Optional[str]) -> pd.DataFrame:
        if not period:
            return self.df

        today = datetime.now()

        days = {
            "week": 7,
            "month": 30,
            "quarter": 90,
            "year": 365
        }.get(period)

        if not days:
            return self.df

        return self.df[self.df["date"] >= today - timedelta(days=days)]


# ------------------------------------------------------------------
# Simple utility helpers
# ------------------------------------------------------------------

def quick_monthly_summary(transactions_df: pd.DataFrame) -> str:
    analytics = FinancialAnalytics(transactions_df)
    stats = analytics.get_summary("month")

    return f"""
📊 Monthly Snapshot
------------------
💵 Income:   ₹{stats['income']:,.2f}
💸 Expenses: ₹{stats['expenses']:,.2f}
💰 Balance:  ₹{stats['balance']:,.2f}
📈 Savings:  {stats['savings_rate']}%
🔢 Entries:  {stats['transactions']}
"""
