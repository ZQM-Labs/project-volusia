from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "Project Volusia Contribution API"
    APP_VERSION: str = "2026-09-03"
    DEBUG: bool = False

    # Database
    DATABASE_URL: str = "sqlite:///./volusia_api.db"

    # Auth — SECRET_KEY MUST be set in production. A hardcoded default would
    # mean any deployment that forgets to override it signs things with a
    # publicly-known value, allowing token forgery. Refuse to start.
    SECRET_KEY: str = ""
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
        # pydantic-settings 2.x defaults to `extra='forbid'`, which made the
        # service crash at import whenever unrelated env vars (e.g.
        # CENSUS_API_KEY/BLS_API_KEY/BEA_API_KEY for the pipeline) were set
        # in the same environment/.env. Ignore unrecognized keys instead.
        extra = "ignore"

    def validate_secret_key(self) -> None:
        """Ensure a non-default SECRET_KEY is present.

        Called at startup; aborts with a clear message instead of silently
        running with a predictable signing key.
        """
        if not self.SECRET_KEY or len(self.SECRET_KEY) < 32 or self.SECRET_KEY == "change-me-in-production":
            raise RuntimeError(
                "SECRET_KEY is not set securely. Generate one with:\n"
                "  python -c \"import secrets; print(secrets.token_urlsafe(64))\"\n"
                "and set it in the environment / .env. Refusing to start insecurely."
            )


settings = Settings()
settings.validate_secret_key()
