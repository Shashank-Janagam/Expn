import os, json
import firebase_admin
from firebase_admin import credentials, firestore

service_account = json.loads(os.environ["FIREBASE_CONFIG"])
cred = credentials.Certificate(service_account)

firebase_admin.initialize_app(cred)
db = firestore.client()
