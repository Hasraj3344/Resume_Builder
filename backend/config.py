"""Configuration settings for the backend application."""

import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./resume_builder.db")

    # JWT Authentication
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # OpenAI API
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

    # PayPal Configuration
    PAYPAL_MODE: str = os.getenv("PAYPAL_MODE", "sandbox")  # sandbox or live
    PAYPAL_CLIENT_ID: str = os.getenv("PAYPAL_CLIENT_ID", "")
    PAYPAL_CLIENT_SECRET: str = os.getenv("PAYPAL_CLIENT_SECRET", "")
    PAYPAL_PRO_PLAN_ID: str = os.getenv("PAYPAL_PRO_PLAN_ID", "")

    # Usage Limits
    FREE_TIER_LIMIT: int = 3  # 3 resumes per month for free tier

    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:8501", "https://localhost:8501"]

    # File Storage
    OUTPUT_DIR: str = "./output/users"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Create settings instance
settings = Settings()


# Validation
def validate_settings():
    """Validate critical settings on startup."""
    if not settings.JWT_SECRET_KEY:
        raise ValueError("JWT_SECRET_KEY environment variable is not set")

    if settings.PAYPAL_MODE == "live":
        if not settings.PAYPAL_CLIENT_ID or not settings.PAYPAL_CLIENT_SECRET:
            raise ValueError("PayPal credentials are required for live mode")

    print("✓ Configuration loaded successfully")
    print(f"  - Database: {settings.DATABASE_URL}")
    print(f"  - PayPal Mode: {settings.PAYPAL_MODE}")
    print(f"  - Free Tier Limit: {settings.FREE_TIER_LIMIT} resumes/month")
