from services.firebase_service import db

def test_firestore_connection():
    collections = db.collections()
    print("Firestore connected. Collections:", collections)

if __name__ == "__main__":
    test_firestore_connection()
