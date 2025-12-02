import os
import google.generativeai as genai
import json
from firebase_config import db
from datetime import datetime

# Configure Gemini API
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Correct: create a model instance  
model = genai.GenerativeModel("gemini-1.5-flash")

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
        Extract expense details and return JSON only.
        Text: '{text}'

        JSON keys: name, amount, category, merchant, date, currency, related.
        - Today's date: {datetime.now().strftime("%Y-%m-%d")}
        - Default currency: INR
        - If date missing → infer
        - If unrelated → related: False
        - Existing categories: [{categories_list}]
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

        return True

    except Exception as e:
        print(f"Error parsing expense: {e}")
        return None
