# services/ai_summary.py

from typing import Dict
import pandas as pd


def build_financial_summary(
    basic_metrics: Dict,
    category_df: pd.DataFrame,
    monthly_df: pd.DataFrame,
    mom_change: float,
) -> str:
    """
    Convert analytics into a compact, human-readable summary
    for Gemini prompts.
    """

    lines = []

    # Basic metrics
    lines.append("Financial Summary:")
    lines.append(f"- Total Income: ₹{basic_metrics['total_income']:.2f}")
    lines.append(f"- Total Expenses: ₹{basic_metrics['total_expenses']:.2f}")
    lines.append(f"- Net Balance: ₹{basic_metrics['net_balance']:.2f}")

    # Category breakdown
    if not category_df.empty:
        lines.append("\nTop Spending Categories:")
        for _, row in category_df.head(3).iterrows():
            lines.append(f"- {row['category']}: ₹{row['amount']:.2f}")

    # Monthly trend
    if not monthly_df.empty:
        latest_month = monthly_df.iloc[-1]
        lines.append(
            f"\nLatest Month ({latest_month['month']}): "
            f"₹{latest_month['amount']:.2f}"
        )

    # MoM change
    if mom_change != 0:
        lines.append(f"Month-over-Month Change: {mom_change}%")

    return "\n".join(lines)
