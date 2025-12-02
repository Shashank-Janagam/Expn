import os
import google.generativeai as genai
import json
from firebase_config import db
from datetime import datetime

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
print("AVAILABLE MODELS:", [m.name for m in genai.list_models()])

# Correct: create a model instance  
model = genai.GenerativeModel("gemini-2.5-flash")

def get_existing_categories(uid):
    categories_ref = db.collection("users").document(uid).collection("categories")
    docs = categories_ref.stream()
    return [doc.id for doc in docs]


def update_user_monthly_total(uid, amount, expense_date):
    try:
        month_key = datetime.strptime(expense_date, "%Y-%m-%d").strftime("%Y-%m")
        month_ref = db.collection("users").document(uid).collection("months").document(month_key)

        snapshot = month_ref.get()
        current_total = snapshot.to_dict().get("total_amount", 0) if snapshot.exists else 0
        new_total = current_total + amount

        month_ref.set({
            "total_amount": new_total,
            "updated_at": datetime.now()
        }, merge=True)

    except Exception as e:
        print(f"Error updating user monthly total: {e}")


def update_category_totals(uid, category, amount, currency, expense_date):
    try:
        month_key = datetime.strptime(expense_date, "%Y-%m-%d").strftime("%Y-%m")
        month_ref = (
            db.collection("users")
              .document(uid)
              .collection("categories")
              .document(category)
              .collection("months")
              .document(month_key)
        )

        snapshot = month_ref.get()
        current_total = snapshot.to_dict().get("total_amount", 0) if snapshot.exists else 0
        new_total = current_total + amount

        month_ref.set({
            "total_amount": new_total,
            "currency": currency,
            "updated_at": datetime.now()
        }, merge=True)

    except Exception as e:
        print(f"Error updating category totals: {e}")


def store_expense_in_category(uid, category, expense_data):
    try:
        db.collection("users") \
          .document(uid) \
          .collection("categories") \
          .document(category) \
          .collection("expenses") \
          .add(expense_data)

    except Exception as e:
        print(f"Error storing expense: {e}")


def parse_expense(uid, text):
    try:
        existing_categories = get_existing_categories(uid)
        categories_list = ", ".join(existing_categories) if existing_categories else "None yet"

        prompt = f"""
        You are an expense-parsing AI. Your ONLY task is to extract expense data.
        OUTPUT must ALWAYS be VALID JSON ONLY.

        USER TEXT: '{text}'

        ==========================
        CATEGORY MATCHING RULES
        ==========================
        Existing categories: [{categories_list}]

        RULES:
        1. ALWAYS match the category with existing categories if the meaning is even close.
        2. If no close match exists, then create a new category — but only as a last resort.
        3. Prefer broad common categories like:
        - Food
        - Groceries
        - Travel
        - Shopping
        - Utilities
        - Entertainment

        ==========================
        RELATED CHECK RULES
        ==========================
        "related": true when:
        - The text expresses spending / paying / buying / costing / amount / price.

        "related": false when:
        - It has NOTHING to do with money or purchase.

        ==========================
        AMOUNT RULES
        ==========================
        - Convert words into numbers (e.g., "hundred" → 100)
        - Keep only numeric value

        ==========================
        DEFAULTS
        ==========================
        - date = today's date if missing ({datetime.now().strftime("%Y-%m-%d")})
        - currency = INR
        - merchant = null if unknown

        ==========================
        JSON SCHEMA
        ==========================
        {{
        "name": string,
        "amount": number,
        "category": string,
        "merchant": string|null,
        "date": "YYYY-MM-DD",
        "currency": "INR",
        "related": boolean
        }}

        ==========================
        EXAMPLES
        ==========================

        Input: "spent 10 for milk"
        Output:
        {{
        "name": "milk",
        "amount": 10,
        "category": "Groceries",
        "merchant": null,
        "date": "{datetime.now().strftime("%Y-%m-%d")}",
        "currency": "INR",
        "related": true
        }}

        Input: "spent hundred for lunch"
        Output:
        {{
        "name": "lunch",
        "amount": 100,
        "category": "Food",
        "merchant": null,
        "date": "{datetime.now().strftime("%Y-%m-%d")}",
        "currency": "INR",
        "related": true
        }}

        Input: "Is it going to rain today?"
        Output:
        {{
        "name": "",
        "amount": 0,
        "category": "",
        "merchant": null,
        "date": "{datetime.now().strftime("%Y-%m-%d")}",
        "currency": "INR",
        "related": false
        }}

        Return ONLY the JSON. No explanation.
        """


        # Correct new API call
        response = model.generate_content(prompt)

        raw_text = response.text.strip()
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start == -1 or end == -1:
            return None

        expense_data = json.loads(raw_text[start:end])

        if not expense_data.get("related", True):
            print("Not related to expense.")
            return False

        if not expense_data.get("date"):
            expense_data["date"] = datetime.now().strftime("%Y-%m-%d")

        category = expense_data.get("category", "Uncategorized")
        amount = float(expense_data.get("amount", 0))
        currency = expense_data.get("currency", "INR")
        expense_date = expense_data["date"]

        store_expense_in_category(uid, category, expense_data)
        update_category_totals(uid, category, amount, currency, expense_date)
        update_user_monthly_total(uid, amount, expense_date)

        return amount

    except Exception as e:
        print(f"Error parsing expense: {e}")
        return False
