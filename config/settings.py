"""
Configuration settings loader for PocketPilot AI
Loads environment variables and validates configuration
(Railway / cloud-safe version)
"""

import os
import json
from dotenv import load_dotenv

# Load environment variables from .env (local only)
load_dotenv()


class Settings:
    """
    Centralized application configuration
    """

    # Gemini Configuration (REQUIRED)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Firebase Configuration (ENV-based, Railway-safe)
    FIREBASE_SERVICE_ACCOUNT_JSON = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")

    # App Configuration
    APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT = int(os.getenv("APP_PORT", 7860))

    @classmethod
    def validate(cls):
        """
        Validate required environment variables
        """

        errors = []

        if not cls.GEMINI_API_KEY:
            errors.append("GEMINI_API_KEY is not set")

        if not cls.FIREBASE_SERVICE_ACCOUNT_JSON:
            errors.append("FIREBASE_SERVICE_ACCOUNT_JSON is not set")
        else:
            try:
                json.loads(cls.FIREBASE_SERVICE_ACCOUNT_JSON)
            except Exception:
                errors.append("FIREBASE_SERVICE_ACCOUNT_JSON is not valid JSON")

        if errors:
            raise ValueError(
                "Configuration errors:\n" +
                "\n".join(f"- {e}" for e in errors)
            )

        return True


# Validate on import
Settings.validate()
