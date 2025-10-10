from google import genai
from firebase_config import db
from datetime import datetime
from firebase_admin import firestore

def get_category_totals_and_transactions(uid, month):
    """
    Fetch category totals and transactions for a given user and month.
    Optimized to reduce unnecessary reads.
    """
    print("Fetching categories for UID:", uid)
    categories_ref = db.collection("users").document(uid).collection("categories")
    categories = {}

    # List category documents
    docs = categories_ref.list_documents()

    for doc in docs:
        cat_name = doc.id

        # Fetch month total directly
        month_snap = doc.collection("months").document(month).get()
        month_data = month_snap.to_dict() or {}
        total = month_data.get("total_amount", 0)

        if total == 0:
            # Skip categories with zero total
            continue

        # Firestore query: only get transactions in this month
        start_date = f"{month}-01"
        end_date = f"{month}-31"

        exp_query = doc.collection("expenses") \
                    .where(field_path="date", op_string=">=", value=start_date) \
                    .where(field_path="date", op_string="<=", value=end_date) \
                    .order_by("date", direction=firestore.Query.DESCENDING) \
                    .stream()

        transactions = []
        for exp in exp_query:
            data = exp.to_dict() or {}
            amount = data.get("amount", 0)
            if amount == 0:
                continue

            transactions.append({
                "expense": amount,
                "timestamp": data.get("date"),
                "name": data.get("name"),
                "merchant": data.get("merchant"),
            })

        categories[cat_name] = {"total": total, "transactions": transactions}

    return categories
