import os
import json
# from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

# Load .env file
# load_dotenv()

service_account = json.loads(os.environ["FIREBASE_CONFIG"])
cred = credentials.Certificate(service_account)

# Avoid reinitializing Firebase
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
