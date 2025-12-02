import firebase_admin
from firebase_admin import credentials, firestore

# Path to your serviceAccountKey.json file
cred = credentials.Certificate("serviceAccountKey.json")

firebase_admin.initialize_app(cred)

db = firestore.client()
