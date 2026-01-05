"""
Firebase Manager for Firestore and Cloud Storage operations
Handles receipt data storage and retrieval
"""

import firebase_admin
from firebase_admin import credentials, firestore, storage
from datetime import datetime
from typing import Dict, List, Optional
import uuid
from config.settings import Settings

class FirebaseManager:
    """Manages Firebase Firestore and Storage operations"""
    
    def __init__(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Initialize Firebase only once
            if not firebase_admin._apps:
                cred = credentials.Certificate(Settings.FIREBASE_SERVICE_ACCOUNT_PATH)
                firebase_admin.initialize_app(cred, {
                    'storageBucket': f"{Settings.GOOGLE_CLOUD_PROJECT_ID}.appspot.com"
                })
            
            # Get Firestore and Storage references
            self.db = firestore.client()
            self.bucket = storage.bucket()
            
            print("✓ Firebase initialized successfully")
        
        except Exception as e:
            print(f"✗ Firebase initialization error: {e}")
            raise
    
    def upload_receipt_file(self, file_path: str, file_name: str) -> str:
        """
        Upload receipt file to Firebase Storage
        
        Args:
            file_path: Local path to the file
            file_name: Original filename
        
        Returns:
            Public URL of the uploaded file
        """
        try:
            # Generate unique filename to prevent collisions
            unique_name = f"receipts/{uuid.uuid4()}_{file_name}"
            
            # Upload file to Firebase Storage
            blob = self.bucket.blob(unique_name)
            blob.upload_from_filename(file_path)
            
            # Make the file publicly accessible (optional - adjust based on security needs)
            blob.make_public()
            
            print(f"✓ File uploaded to Storage: {unique_name}")
            return blob.public_url
        
        except Exception as e:
            print(f"✗ Storage upload error: {e}")
            raise
    
    def save_receipt_data(self, receipt_data: Dict) -> str:
        """
        Save extracted receipt data to Firestore
        
        Args:
            receipt_data: Dictionary containing receipt information
        
        Returns:
            Document ID of the saved receipt
        """
        try:
            # Add timestamp
            receipt_data['created_at'] = datetime.now()
            receipt_data['updated_at'] = datetime.now()
            
            # Save to Firestore
            doc_ref = self.db.collection(Settings.RECEIPTS_COLLECTION).add(receipt_data)
            doc_id = doc_ref[1].id
            
            print(f"✓ Receipt saved to Firestore: {doc_id}")
            return doc_id
        
        except Exception as e:
            print(f"✗ Firestore save error: {e}")
            raise
    
    def get_all_receipts(self) -> List[Dict]:
        """
        Retrieve all receipts from Firestore
        
        Returns:
            List of receipt dictionaries
        """
        try:
            receipts = []
            
            # Query all receipts, ordered by date
            docs = self.db.collection(Settings.RECEIPTS_COLLECTION)\
                         .order_by('created_at', direction=firestore.Query.DESCENDING)\
                         .stream()
            
            for doc in docs:
                receipt = doc.to_dict()
                receipt['id'] = doc.id
                
                # Convert Firestore timestamps to strings for display
                if 'created_at' in receipt:
                    receipt['created_at'] = receipt['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                
                receipts.append(receipt)
            
            print(f"✓ Retrieved {len(receipts)} receipts from Firestore")
            return receipts
        
        except Exception as e:
            print(f"✗ Firestore retrieval error: {e}")
            return []
    
    def get_receipt_by_id(self, receipt_id: str) -> Optional[Dict]:
        """
        Retrieve a specific receipt by ID
        
        Args:
            receipt_id: Firestore document ID
        
        Returns:
            Receipt dictionary or None if not found
        """
        try:
            doc = self.db.collection(Settings.RECEIPTS_COLLECTION).document(receipt_id).get()
            
            if doc.exists:
                receipt = doc.to_dict()
                receipt['id'] = doc.id
                return receipt
            else:
                return None
        
        except Exception as e:
            print(f"✗ Firestore get error: {e}")
            return None
    
    def delete_receipt(self, receipt_id: str) -> bool:
        """
        Delete a receipt from Firestore
        
        Args:
            receipt_id: Firestore document ID
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.db.collection(Settings.RECEIPTS_COLLECTION).document(receipt_id).delete()
            print(f"✓ Receipt deleted: {receipt_id}")
            return True
        
        except Exception as e:
            print(f"✗ Firestore delete error: {e}")
            return False