from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from .config import get_settings
from . import models


def cleanup_old_data(db: Session) -> int:
    """
    Delete documents and metrics older than the configured retention window.
    """
    settings = get_settings()
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.data_retention_days)

    deleted = 0

    deleted_docs = (
        db.query(models.Document)
        .filter(models.Document.created_at < cutoff)
        .delete(synchronize_session=False)
    )
    deleted += deleted_docs

    deleted_ga = (
        db.query(models.GaDailyMetric)
        .filter(models.GaDailyMetric.date < cutoff)
        .delete(synchronize_session=False)
    )
    deleted += deleted_ga

    deleted_gsc = (
        db.query(models.GscDailyMetric)
        .filter(models.GscDailyMetric.date < cutoff)
        .delete(synchronize_session=False)
    )
    deleted += deleted_gsc

    db.commit()
    return deleted

