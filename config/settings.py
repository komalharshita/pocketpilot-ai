"""
Configuration settings loader for PocketPilot AI
Loads environment variables and validates configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Settings:
    """
    Centralized application configuration
    """

    # Gemini Configuration (REQUIRED)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT_PATH = os.getenv(
        "FIREBASE_SERVICE_ACCOUNT_PATH",
        "./serviceAccountKey.json"
    )

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

        if not os.path.exists(cls.FIREBASE_SERVICE_ACCOUNT_PATH):
            errors.append(
                f"Firebase service account not found at "
                f"{cls.FIREBASE_SERVICE_ACCOUNT_PATH}"
            )

        if errors:
            raise ValueError(
                "Configuration errors:\n" +
                "\n".join(f"- {e}" for e in errors)
            )

        return True


# Validate on import
Settings.validate()
