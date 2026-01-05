"""
Configuration settings loader for PocketPilot AI
Loads environment variables and validates configuration
"""

import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings loaded from environment variables"""
    
    # Google Cloud Configuration
    GOOGLE_CLOUD_PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT_ID")
    DOCUMENT_AI_PROCESSOR_ID = os.getenv("DOCUMENT_AI_PROCESSOR_ID")
    DOCUMENT_AI_LOCATION = os.getenv("DOCUMENT_AI_LOCATION", "us")
    
    # Gemini API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-1.5-pro"
    
    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH", 
        "./serviceAccountKey.json"
    )
    
    # Application Configuration
    APP_PORT = int(os.getenv("APP_PORT", 7860))
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    
    # Firestore Collections
    RECEIPTS_COLLECTION = "receipts"
    
    # Firebase Storage Bucket (auto-detected from service account)
    STORAGE_BUCKET = None
    
    @classmethod
    def validate(cls):
        """Validate that all required settings are present"""
        errors = []
        
        if not cls.GOOGLE_CLOUD_PROJECT_ID:
            errors.append("GOOGLE_CLOUD_PROJECT_ID is not set")
        
        if not cls.DOCUMENT_AI_PROCESSOR_ID:
            errors.append("DOCUMENT_AI_PROCESSOR_ID is not set")
        
        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set")
        
        if not Path(cls.FIREBASE_SERVICE_ACCOUNT_PATH).exists():
            errors.append(f"Firebase service account file not found at {cls.FIREBASE_SERVICE_ACCOUNT_PATH}")
        
        if errors:
            raise ValueError(f"Configuration errors:\n" + "\n".join(f"  - {e}" for e in errors))
        
        return True

# Validate settings on import
Settings.validate()