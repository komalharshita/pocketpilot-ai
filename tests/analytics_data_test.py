from services.analytics_data import get_transactions_df

TEST_USER_ID = "test-user-uid"

if __name__ == "__main__":
    df = get_transactions_df(TEST_USER_ID)
    print(df.head())
    print("Rows:", len(df))
    print("Columns:", list(df.columns))
