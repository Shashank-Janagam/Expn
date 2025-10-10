from google import genai
import json
from firebase_config import db
from datetime import datetime

client = genai.Client(api_key="AIzaSyB18-oAXbC6Y26-QZb-0jMy2EGd6RV2rig")

def get_existing_categories(uid):
    """Fetch all categories for a user from Firestore"""
    categories_ref = db.collection("users").document(uid).collection("categories")
    docs = categories_ref.stream()
    return [doc.id for doc in docs]  # category names are document IDs
def update_user_monthly_total(uid, amount, expense_date):
    """Update the user's total expenditure for the month"""
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

        print(f"Updated user {uid} total for {month_key}: +{amount}")

    except Exception as e:
        print(f"Error updating user monthly total: {e}")

def update_category_totals(uid, category, amount, currency, expense_date):
    """Update monthly totals per category in Firestore"""
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

        print(f"Updated {category} total for {month_key}: +{amount} {currency}")

    except Exception as e:
        print(f"Error updating category totals: {e}")

def store_expense_in_category(uid, category, expense_data):
    """
    Store the expense directly under its category with timestamped doc ID
    """
    try:
        # Document ID can be auto-generated or based on timestamp
        db.collection("users") \
          .document(uid) \
          .collection("categories") \
          .document(category) \
          .collection("expenses") \
          .add(expense_data)
        print(f"Stored expense in category '{category}'")
    except Exception as e:
        print(f"Error storing expense: {e}")

def parse_expense(uid, text):
    """
    Parse text with Gemini, store expense in category, and update monthly totals.
    """
    try:
        existing_categories = get_existing_categories(uid)
        categories_list = ", ".join(existing_categories) if existing_categories else "None yet"

        prompt = f"""
        Extract expense details from the following text and respond ONLY in JSON format.
        Text: '{text}'
        
        JSON keys: name, amount, category, merchant, date, currency, related.

        - Today's date is {datetime.now().strftime("%Y-%m-%d")}.
        - Default currency: INR.
        - If no date is mentioned, infer (yesterday, last Monday, etc.).
        - If not an expense → related: False else True.
        - Available categories: [{categories_list}]. 
        - If the expense fits one of them, pick it. 
        - If none fit, create a new category.
        """

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        raw_text = response.text.strip()
        start = raw_text.find("{")
        end = raw_text.rfind("}") + 1
        if start == -1 or end == -1:
            return None

        expense_data = json.loads(raw_text[start:end])
        if not expense_data.get("related", True):
            print("Not related to expense.")
            return False

        # Ensure date exists
        if not expense_data.get("date"):
            expense_data["date"] = datetime.now().strftime("%Y-%m-%d")

        category = expense_data.get("category", "Uncategorized")
        amount = float(expense_data.get("amount", 0))
        currency = expense_data.get("currency", "INR")
        expense_date = expense_data["date"]

        # Store in the respective category
        store_expense_in_category(uid, category, expense_data)

        # Update monthly totals
        update_category_totals(uid, category, amount, currency, expense_date)
        update_user_monthly_total(uid, amount, expense_date)
        return True

    except Exception as e:
        print(f"Error parsing expense: {e}")
        return None
