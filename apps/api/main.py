from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import db, models, schemas
from .deps import get_request_context
from .routers import router as core_router

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
    # Ensure a default dev tenant exists so frontend (X-Tenant-Id: 1) works.
    with db.SessionLocal() as session:
        if session.query(models.Tenant).first() is None:
            session.add(models.Tenant(name="Foundation for Shared Impact", is_active=True))
            session.commit()


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


