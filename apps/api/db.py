from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import get_settings


settings = get_settings()


class Base(DeclarativeBase):
    pass


_engine_kw: dict = {"echo": settings.api_debug}
if settings.database_url.startswith("sqlite"):
    # Required when FastAPI uses one SQLite connection per request thread.
    _engine_kw["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **_engine_kw)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

