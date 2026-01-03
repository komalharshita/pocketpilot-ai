from datetime import datetime
from services.transaction_service import create_transaction, get_user_transactions

TEST_USER_ID = "test-user-uid"

payload = {
    "user_id": TEST_USER_ID,
    "type": "expense",
    "amount": 250,
    "category": "Food",
    "date": datetime.utcnow(),
    "notes": "Lunch",
    "source": "manual",
}

if __name__ == "__main__":
    tid = create_transaction(payload)
    print("Created transaction:", tid)

    txns = get_user_transactions(TEST_USER_ID)
    print("Fetched transactions:", len(txns))
