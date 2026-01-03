from services.ai_summary import build_financial_summary
from services.ai_prompt import build_prompt
from services.gemini_service import generate_response
from services.analytics_data import get_transactions_df
from services.analytics_metrics import (
    compute_basic_metrics,
    compute_category_totals,
    compute_monthly_totals,
    compute_month_over_month_change,
)

TEST_USER_ID = "test-user-uid"

if __name__ == "__main__":
    df = get_transactions_df(TEST_USER_ID)

    basic = compute_basic_metrics(df)
    category = compute_category_totals(df)
    monthly = compute_monthly_totals(df)
    mom = compute_month_over_month_change(monthly)

    summary = build_financial_summary(basic, category, monthly, mom)
    prompt = build_prompt(summary, "How can I save more money?")

    print("----- PROMPT -----")
    print(prompt)

    print("\n----- GEMINI RESPONSE -----")
    response = generate_response(prompt)
    print(response)
