import os
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field

# Load .env from project root so LLM and DB env vars work when API is started by uvicorn --reload.
# This file lives at apps/api/config.py, so project root is three levels up.
try:
    from dotenv import load_dotenv

    _env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(_env_path)
except ImportError:
    # If python-dotenv is not installed, we simply fall back to OS env vars.
    pass


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _resolve_database_url() -> str:
    """
    Resolution order:

    1. **USE_SQLITE_FOR_DEV** (`true` / `1` / `yes`) — forces repo-local SQLite
       (`data/dev.sqlite`). Wins even if `DATABASE_URL` is set in `.env`, so you
       can keep Postgres URLs on disk but still run the API without Docker.
    2. **DATABASE_URL** — explicit Postgres or other backend.
    3. Default — PostgreSQL on localhost (Docker Compose credentials).
    """
    flag = os.getenv("USE_SQLITE_FOR_DEV", "").strip().lower()
    if flag in ("1", "true", "yes"):
        data_dir = _REPO_ROOT / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = (data_dir / "dev.sqlite").resolve()
        return f"sqlite:///{db_path.as_posix()}"

    explicit = os.getenv("DATABASE_URL")
    if explicit:
        return explicit.strip()

    return (
        "postgresql+psycopg2://charity:charity_dev@localhost:5432/charity_insights"
    )


class Settings(BaseModel):
    database_url: str = Field(default_factory=_resolve_database_url)
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

    # LLM: Ollama only (local, OpenAI-compatible /v1 endpoint)
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434/v1")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "llama3.2")
    ollama_api_key: str = os.getenv("OLLAMA_API_KEY", "ollama")


@lru_cache
def get_settings() -> Settings:
    return Settings()
