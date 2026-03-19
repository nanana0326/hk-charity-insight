import logging

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from . import db, models, schemas
from .config import get_settings
from .deps import get_request_context
from .routers import router as core_router
from .auth import router as auth_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="HK Charity Insights API",
    description="APIs for document analysis, insights, and traffic analytics.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    # Create tables on first run; in real deployment this should be via migrations.
    models.Base.metadata.create_all(bind=db.engine)  # type: ignore[arg-type]
    # Lightweight migrations.
    with db.engine.connect() as conn:  # type: ignore[arg-type]
        try:
            # Ensure per-user ownership field exists on documents.
            conn.execute(
                text(
                    "ALTER TABLE documents "
                    "ADD COLUMN IF NOT EXISTS created_by_user_id INTEGER NULL"
                )
            )
            # Ensure password-based auth fields exist on users.
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN IF NOT EXISTS password_hash VARCHAR(255) NULL"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN IF NOT EXISTS reset_token VARCHAR(255) NULL"
                )
            )
            conn.execute(
                text(
                    "ALTER TABLE users "
                    "ADD COLUMN IF NOT EXISTS reset_token_expires_at TIMESTAMPTZ NULL"
                )
            )
            conn.commit()
        except Exception:
            logger.exception("Failed to run lightweight migrations")
    # Ensure a default dev tenant exists so frontend (X-Tenant-Id: 1) works.
    with db.SessionLocal() as session:
        if session.query(models.Tenant).first() is None:
            session.add(models.Tenant(name="Foundation for Shared Impact", is_active=True))
            session.commit()

    settings = get_settings()
    logger.info(
        "DeepSeek API key configured: %s (set DEEPSEEK_API_KEY in this process if False)",
        bool(settings.deepseek_api_key),
    )


app.include_router(auth_router, prefix="/api")
app.include_router(core_router, prefix="/api")


@app.get("/health", tags=["system"])
async def health() -> dict:
    return {"status": "ok"}


@app.get("/", tags=["system"])
async def root(ctx: schemas.RequestContext = Depends(get_request_context)) -> dict:
    return {
        "service": "hk-charity-insights-api",
        "version": "0.1.0",
        "tenant_id": ctx.tenant_id,
        "role": ctx.role,
    }


