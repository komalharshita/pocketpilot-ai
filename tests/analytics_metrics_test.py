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
    print("Basic Metrics:", basic)

    category = compute_category_totals(df)
    print("\nCategory Totals:")
    print(category)

    monthly = compute_monthly_totals(df)
    print("\nMonthly Totals:")
    print(monthly)

    mom = compute_month_over_month_change(monthly)
    print("\nMoM Change:", mom, "%")
