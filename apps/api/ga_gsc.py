from datetime import datetime, timedelta, timezone
from typing import Iterable, List

from sqlalchemy.orm import Session

from . import models, schemas


def _get_credential(
    db: Session, *, tenant_id: int, provider: models.GoogleProvider
) -> models.GoogleCredential | None:
    return (
        db.query(models.GoogleCredential)
        .filter(
            models.GoogleCredential.tenant_id == tenant_id,
            models.GoogleCredential.provider == provider,
        )
        .order_by(models.GoogleCredential.id.desc())
        .first()
    )


def collect_ga_stub(
    db: Session,
    *,
    tenant_id: int,
    property_id: str,
    days: int = 30,
) -> int:
    """
    Stub implementation that synthesizes GA-style daily metrics.

    This creates simple rising time series data as a placeholder until
    real GA4 API integration is wired in.
    """
    cred = _get_credential(db, tenant_id=tenant_id, provider=models.GoogleProvider.ANALYTICS)
    if cred is None:
        return 0

    today = datetime.now(timezone.utc).date()
    created = 0
    for offset in range(days):
        d = today - timedelta(days=offset)
        dt = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
        metric = models.GaDailyMetric(
            tenant_id=tenant_id,
            date=dt,
            property_id=property_id,
            sessions=100 + offset * 2,
            users=80 + offset,
            pageviews=200 + offset * 3,
        )
        db.add(metric)
        created += 1

    db.commit()
    return created


def collect_gsc_stub(
    db: Session,
    *,
    tenant_id: int,
    site_url: str,
    days: int = 30,
) -> int:
    """
    Stub implementation that synthesizes GSC-style daily metrics.
    """
    cred = _get_credential(
        db, tenant_id=tenant_id, provider=models.GoogleProvider.SEARCH_CONSOLE
    )
    if cred is None:
        return 0

    today = datetime.now(timezone.utc).date()
    created = 0
    for offset in range(days):
        d = today - timedelta(days=offset)
        dt = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
        ctr = 0.05 + offset * 0.0005
        position = 8.0 - offset * 0.02
        metric = models.GscDailyMetric(
            tenant_id=tenant_id,
            date=dt,
            site_url=site_url,
            clicks=50 + offset,
            impressions=1000 + offset * 5,
            ctr=ctr,
            position=position,
        )
        db.add(metric)
        created += 1

    db.commit()
    return created


def build_web_impact_summary(
    db: Session,
    *,
    tenant_id: int,
    days: int = 30,
) -> schemas.WebImpactSummary:
    since = datetime.now(timezone.utc) - timedelta(days=days)

    ga_rows: list[models.GaDailyMetric] = (
        db.query(models.GaDailyMetric)
        .filter(
            models.GaDailyMetric.tenant_id == tenant_id,
            models.GaDailyMetric.date >= since,
        )
        .order_by(models.GaDailyMetric.date.asc())
        .all()
    )

    gsc_rows: list[models.GscDailyMetric] = (
        db.query(models.GscDailyMetric)
        .filter(
            models.GscDailyMetric.tenant_id == tenant_id,
            models.GscDailyMetric.date >= since,
        )
        .order_by(models.GscDailyMetric.date.asc())
        .all()
    )

    dates = [row.date.date().isoformat() for row in ga_rows]
    sessions = [row.sessions for row in ga_rows]
    clicks = [row.clicks for row in gsc_rows]

    charts: List[schemas.ChartSpec] = []

    if ga_rows:
        charts.append(
            schemas.ChartSpec(
                id="ga_sessions_trend",
                type=schemas.ChartType.LINE,
                title="Website sessions trend (recent period)",
                description="A time series of website sessions based on GA data, to observe overall traffic trends.",
                data={
                    "x": dates,
                    "series": [
                        {"name": "sessions", "data": sessions},
                    ],
                },
            )
        )

    if gsc_rows:
        charts.append(
            schemas.ChartSpec(
                id="gsc_clicks_trend",
                type=schemas.ChartType.LINE,
                title="Search clicks trend (recent period)",
                description="A time series of search clicks based on Search Console data, to observe changes in organic search visibility.",
                data={
                    "x": [row.date.date().isoformat() for row in gsc_rows],
                    "series": [
                        {"name": "clicks", "data": clicks},
                    ],
                },
            )
        )

    summary = (
        "Web impact report (MVP): based on recent trends in sessions and search clicks, "
        "this view helps organisations quickly understand overall traffic and search visibility. "
        "Future iterations can add breakdowns by channel, top pages and high-potential search terms."
    )

    return schemas.WebImpactSummary(
        title="Organisation web impact overview",
        summary=summary,
        charts=charts,
    )

