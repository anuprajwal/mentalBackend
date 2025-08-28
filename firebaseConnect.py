from firebase_admin import credentials, firestore
import firebase_admin


cred = credentials.Certificate("mentaldb-7492d-firebase-adminsdk-fbsvc-2ca121043d.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
