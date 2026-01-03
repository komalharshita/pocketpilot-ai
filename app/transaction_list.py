# app/transaction_list.py

import streamlit as st
from services.transaction_service import (
    get_user_transactions,
    delete_transaction
)

def transaction_list(user):
    st.subheader("Your Transactions")

    user_id = user["localId"]
    transactions = get_user_transactions(user_id)

    if not transactions:
        st.info("No transactions added yet.")
        return

    for txn in transactions:
        with st.container():
            cols = st.columns([3, 2, 2, 2, 1])

            cols[0].write(txn["category"])
            cols[1].write(txn["type"].capitalize())
            cols[2].write(f"₹{txn['amount']}")
            cols[3].write(txn["date"].strftime("%Y-%m-%d"))

            if cols[4].button("Delete", key=txn["transaction_id"]):
                delete_transaction(user_id, txn["transaction_id"])
                st.success("Transaction deleted.")
                st.experimental_rerun()
