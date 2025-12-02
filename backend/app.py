# app.py
from flask import Flask, request, jsonify, redirect
from firebase_config import db
from firebase_admin import auth
from flask_cors import CORS
import requests
import json
from gemini_int import parse_expense

from getData import get_category_totals_and_transactions

app = Flask(__name__)
CORS(app)

# # Load Google OAuth JSON config
# with open("OAuth.json") as f:
#     google_config = json.load(f)["installed"]

# CLIENT_ID = google_config["client_id"]
# CLIENT_SECRET = google_config["client_secret"]
# REDIRECT_URI = "http://localhost:5000/oauth2callback"
# TOKEN_URI = google_config["token_uri"]
# SCOPES = "https://www.googleapis.com/auth/gmail.readonly"

# ------------------ Firebase Token Verification ------------------


# ------------------ Login Verification ------------------
@app.route("/verify_login", methods=["POST"])
def verify_login():
    data = request.json
    id_token = data.get("idToken")
    if not id_token:
        return jsonify({"error": "No ID token"}), 400
    try:
        decoded = auth.verify_id_token(id_token)
        uid = decoded["uid"]
        email = decoded.get("email", "")
        name = decoded.get("name", "")

        db.collection("users").document(uid).set({
            "name": name,
            "email": email
        }, merge=True)

        # Check if Gmail token exists
        user_doc = db.collection("users").document(uid).get()
        has_token = "gmail_refresh_token" in user_doc.to_dict() if user_doc.exists else False

        return jsonify({"success": True, "uid": uid, "requireGmailConsent": not has_token})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# ------------------ Gmail Consent Flow ------------------




# ------------------ Check Gmail Token ------------------

# ------------------ Expense Routes ------------------
@app.route("/add_expense", methods=["POST"])
def add_expense():
    data = request.json

    res=parse_expense(data["uid"],data["text"])
    return jsonify(res)

@app.route("/get_expenses", methods=["GET"])
def get_expenses():
    expenses = []
    docs = db.collection("expenses").stream()
    for doc in docs:
        expenses.append(doc.to_dict())
    return jsonify(expenses)

@app.route("/get_categories", methods=["GET"])
def get_categories():
    uid = request.args.get("uid")
    month=request.args.get("month")
    print("Request received for UID:", uid)  # should print the actual UID
    if not uid:
        return jsonify({"error":"uid required"}),400
    try:

        categories = get_category_totals_and_transactions(uid,month)

        return jsonify(categories)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/get_user_month_total", methods=["GET"])
def get_user_month_total():
    try:
        uid = request.args.get("uid")
        month = request.args.get("month")  # "YYYY-MM"
        if not uid or not month:
            return jsonify({"error": "uid and month required"}), 400

        # Reference to the month document under user's months
        month_ref = (
            db.collection("users")
              .document(uid)
              .collection("months")
              .document(month)
        )
        snapshot = month_ref.get()
        total = snapshot.to_dict().get("total_amount", 0) if snapshot.exists else 0

        return jsonify({"total": total})

    except Exception as e:
        print("Error fetching month total:", e)
        return jsonify({"error": str(e)}), 500



# ------------------ Home ------------------
@app.route("/")
def home():
    return "Backend is running!"

if __name__ == "__main__":
    app.run(debug=True)
