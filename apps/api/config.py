import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel

# Load .env from project root so DEEPSEEK_API_KEY works even when API is started by uvicorn --reload.
# This file lives at apps/api/config.py, so project root is three levels up.
try:
    from dotenv import load_dotenv

    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    # If python-dotenv is not installed, we simply fall back to OS env vars.
    pass


class Settings(BaseModel):
    database_url: str = (
        os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://charity:charity_dev@localhost:5432/charity_insights",
        )
    )
    api_debug: bool = os.getenv("API_DEBUG", "true").lower() == "true"

    google_client_id: str | None = os.getenv("GOOGLE_CLIENT_ID")
    google_client_secret: str | None = os.getenv("GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str | None = os.getenv("GOOGLE_REDIRECT_URI")

    google_analytics_scopes: list[str] = [
        "https://www.googleapis.com/auth/analytics.readonly"
    ]
    google_search_console_scopes: list[str] = [
        "https://www.googleapis.com/auth/webmasters.readonly"
    ]

    data_retention_days: int = int(os.getenv("DATA_RETENTION_DAYS", "180"))

    web_base_url: str = os.getenv("WEB_BASE_URL", "http://localhost:3000")
    smtp_host: str | None = os.getenv("SMTP_HOST")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str | None = os.getenv("SMTP_USER")
    smtp_password: str | None = os.getenv("SMTP_PASSWORD")
    smtp_from_email: str | None = os.getenv("SMTP_FROM_EMAIL")
    smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    smtp_use_ssl: bool = os.getenv("SMTP_USE_SSL", "false").lower() == "true"

    # LLM / DeepSeek
    deepseek_api_key: str | None = os.getenv("DEEPSEEK_API_KEY")
    deepseek_model: str = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-chat")
    deepseek_base_url: str = os.getenv(
        "DEEPSEEK_BASE_URL", "https://api.deepseek.com"
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

