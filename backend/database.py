import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resume-9e979-firebase-adminsdk-fbsvc-d2f54c1e0e.json")

# Prevent double initialization in hot-reload environments like FastAPI
if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

# Export Firestore database client
db = firestore.client()
