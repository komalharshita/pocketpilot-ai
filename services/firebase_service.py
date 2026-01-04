"""
Firebase Service - Handle Firestore and Storage operations
Manages receipt data storage and file uploads
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict, Optional
import uuid

try:
    import firebase_admin
    from firebase_admin import credentials, firestore, storage
    FIREBASE_AVAILABLE = True
except ImportError:
    FIREBASE_AVAILABLE = False


class FirebaseService:
    """
    Service for Firebase operations
    - Firestore: Store receipt metadata
    - Storage: Store receipt images/PDFs
    """
    
    def __init__(self):
        """Initialize Firebase app if credentials are available"""
        if not FIREBASE_AVAILABLE:
            raise ImportError("firebase-admin not installed")
        
        # Initialize Firebase app if not already done
        if not firebase_admin._apps:
            try:
                # Try to load from Streamlit secrets
                firebase_config = st.secrets.get("firebase", None)
                
                if firebase_config:
                    # Use service account from secrets
                    cred = credentials.Certificate(dict(firebase_config))
                    firebase_admin.initialize_app(cred, {
                        'storageBucket': firebase_config.get('storage_bucket', '')
                    })
                else:
                    # Try default credentials (for local development)
                    cred = credentials.ApplicationDefault()
                    firebase_admin.initialize_app(cred)
                    
            except Exception as e:
                raise ValueError(f"Failed to initialize Firebase: {str(e)}")
        
        # Get Firestore and Storage clients
        self.db = firestore.client()
        try:
            self.bucket = storage.bucket()
        except:
            self.bucket = None
    
    # ========================================================================
    # RECEIPT OPERATIONS
    # ========================================================================
    
    def save_receipt(self, receipt_data: Dict) -> bool:
        """
        Save receipt data to Firestore
        
        Args:
            receipt_data: Dictionary containing receipt information
            
        Returns:
            bool: Success status
        """
        try:
            receipt_id = receipt_data.get('id', str(uuid.uuid4()))
            
            # Add timestamp
            receipt_data['created_at'] = firestore.SERVER_TIMESTAMP
            receipt_data['updated_at'] = firestore.SERVER_TIMESTAMP
            
            # Save to Firestore
            self.db.collection('receipts').document(receipt_id).set(receipt_data)
            
            return True
            
        except Exception as e:
            st.error(f"Error saving receipt: {str(e)}")
            return False
    
    def get_all_receipts(self) -> List[Dict]:
        """
        Retrieve all receipts from Firestore
        
        Returns:
            List of receipt dictionaries
        """
        try:
            receipts = []
            docs = self.db.collection('receipts').stream()
            
            for doc in docs:
                receipt = doc.to_dict()
                receipt['id'] = doc.id
                receipts.append(receipt)
            
            return receipts
            
        except Exception as e:
            st.error(f"Error fetching receipts: {str(e)}")
            return []
    
    def get_receipt(self, receipt_id: str) -> Optional[Dict]:
        """
        Get a specific receipt by ID
        
        Args:
            receipt_id: Receipt document ID
            
        Returns:
            Receipt dictionary or None
        """
        try:
            doc = self.db.collection('receipts').document(receipt_id).get()
            
            if doc.exists:
                receipt = doc.to_dict()
                receipt['id'] = doc.id
                return receipt
            
            return None
            
        except Exception as e:
            st.error(f"Error fetching receipt: {str(e)}")
            return None
    
    def delete_receipt(self, receipt_id: str) -> bool:
        """
        Delete a receipt from Firestore
        
        Args:
            receipt_id: Receipt document ID
            
        Returns:
            bool: Success status
        """
        try:
            self.db.collection('receipts').document(receipt_id).delete()
            return True
            
        except Exception as e:
            st.error(f"Error deleting receipt: {str(e)}")
            return False
    
    # ========================================================================
    # FILE STORAGE OPERATIONS
    # ========================================================================
    
    def upload_file(
        self, 
        file_bytes: bytes, 
        filename: str, 
        mime_type: str
    ) -> Optional[str]:
        """
        Upload file to Firebase Storage
        
        Args:
            file_bytes: File content as bytes
            filename: Original filename
            mime_type: MIME type of file
            
        Returns:
            Public URL of uploaded file or None
        """
        if not self.bucket:
            st.warning("Storage bucket not configured")
            return None
        
        try:
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            unique_filename = f"receipts/{timestamp}_{filename}"
            
            # Upload to Storage
            blob = self.bucket.blob(unique_filename)
            blob.upload_from_string(file_bytes, content_type=mime_type)
            
            # Make public
            blob.make_public()
            
            return blob.public_url
            
        except Exception as e:
            st.error(f"Error uploading file: {str(e)}")
            return None
    
    def delete_file(self, file_url: str) -> bool:
        """
        Delete file from Firebase Storage
        
        Args:
            file_url: Public URL of file
            
        Returns:
            bool: Success status
        """
        if not self.bucket:
            return False
        
        try:
            # Extract blob name from URL
            blob_name = file_url.split('/')[-1]
            blob = self.bucket.blob(f"receipts/{blob_name}")
            blob.delete()
            
            return True
            
        except Exception as e:
            st.error(f"Error deleting file: {str(e)}")
            return False
