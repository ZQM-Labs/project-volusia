import os
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Project Volusia Contribution API"
    APP_VERSION: str = "2026-09-03"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./volusia_api.db"

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # Rate limiting
    RATE_LIMIT_DEFAULT: int = 100  # requests per window
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour in seconds

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    # File upload
    MAX_UPLOAD_SIZE: int = 5 * 1024 * 1024  # 5MB

    class Config:
        env_file = ".env"

settings = Settings()
