import os
from functools import lru_cache

from pydantic import BaseModel


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


@lru_cache
def get_settings() -> Settings:
    return Settings()

