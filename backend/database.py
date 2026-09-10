import os
import json
import firebase_admin
from firebase_admin import credentials, firestore

# Prevent double initialization in hot-reload environments like FastAPI
if not firebase_admin._apps:
    firebase_creds_str = os.environ.get("FIREBASE_CREDENTIALS")
    if firebase_creds_str:
        # Load from environment variable (Production on Render)
        cred_dict = json.loads(firebase_creds_str)
        cred = credentials.Certificate(cred_dict)
    else:
        # Load from local file (Local Development)
        cred_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "resume-9e979-firebase-adminsdk-fbsvc-d2f54c1e0e.json")
        cred = credentials.Certificate(cred_path)
        
    firebase_admin.initialize_app(cred)

# Export Firestore database client
db = firestore.client()

