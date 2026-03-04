from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from . import analysis, audit, ga_gsc, google_oauth, ingest, maintenance, models, schemas
from .db import get_db
from .deps import get_request_context, require_internal_actor, require_public_view


router = APIRouter()


@router.post(
    "/tenants",
    response_model=schemas.TenantRead,
    tags=["tenants"],
)
def create_tenant(
    payload: schemas.TenantCreate,
    db: Session = Depends(get_db),
) -> schemas.TenantRead:
    tenant = models.Tenant(name=payload.name, is_active=True)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return schemas.TenantRead.model_validate(tenant)


@router.get(
    "/tenants/me",
    response_model=schemas.TenantRead,
    tags=["tenants"],
)
def get_my_tenant(
    ctx: schemas.RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> schemas.TenantRead:
    tenant = db.get(models.Tenant, ctx.tenant_id)
    assert tenant is not None  # validated in dependency
    return schemas.TenantRead.model_validate(tenant)


@router.post(
    "/tenants/{tenant_id}/users",
    response_model=schemas.UserRead,
    tags=["users"],
)
def create_user_for_tenant(
    tenant_id: int,
    payload: schemas.UserBase,
    db: Session = Depends(get_db),
    _: schemas.RequestContext = Depends(require_internal_actor),
) -> schemas.UserRead:
    user = models.User(
        tenant_id=tenant_id,
        email=payload.email,
        display_name=payload.display_name,
        role=models.UserRole(payload.role.value),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return schemas.UserRead.model_validate(user)


@router.get(
    "/documents",
    response_model=schemas.DocumentListResponse,
    tags=["documents"],
)
def list_documents(
    ctx: schemas.RequestContext = Depends(get_request_context),
    db: Session = Depends(get_db),
) -> schemas.DocumentListResponse:
    rows = (
        db.query(models.Document)
        .filter(models.Document.tenant_id == ctx.tenant_id)
        .order_by(models.Document.created_at.desc())
        .all()
    )
    items = [
        schemas.DocumentListItem(
            id=d.id,
            original_filename=d.original_filename,
            doc_type=schemas.DocumentType(d.doc_type.value),
            created_at=d.created_at.isoformat() if d.created_at else "",
        )
        for d in rows
    ]
    return schemas.DocumentListResponse(documents=items)


@router.post(
    "/documents/upload",
    response_model=schemas.DocumentUploadResponse,
    tags=["documents"],
)
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("other"),
    ctx: schemas.RequestContext = Depends(require_public_view),
    db: Session = Depends(get_db),
) -> schemas.DocumentUploadResponse:
    """
    Entry point for document ingestion.

    For now this runs synchronously; later it can be delegated to a background worker.
    """
    allowed_types = {
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "text/csv",
        "application/csv",
        "text/comma-separated-values",
    }
    # Also allow by extension for CSV (browsers may send application/octet-stream)
    if file.content_type not in allowed_types:
        fn = (file.filename or "").lower()
        if not fn.endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file type",
            )

    document = ingest.ingest_document(
        db,
        tenant_id=ctx.tenant_id,
        upload=file,
        doc_type=models.DocumentType(doc_type) if doc_type in ("annual_report", "application", "project_report", "other") else models.DocumentType.OTHER,
    )
    pages_count = len(document.pages)
    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="document_uploaded",
        resource_type="document",
        resource_id=str(document.id),
        actor_role=ctx.role.value,
        metadata={"pages": pages_count, "mime_type": file.content_type},
    )
    return schemas.DocumentUploadResponse(document_id=document.id, pages=pages_count)


@router.api_route(
    "/documents/{document_id}/analyze",
    methods=["GET", "POST"],
    response_model=schemas.InsightReport,
    tags=["documents", "analysis"],
)
async def analyze_document(
    document_id: int,
    mode: schemas.AnalysisMode = schemas.AnalysisMode.FUNDER,
    ctx=Depends(get_request_context),
    db: Session = Depends(get_db),
) -> schemas.InsightReport:
    document = db.get(models.Document, document_id)
    if document is None or document.tenant_id != ctx.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    if mode == schemas.AnalysisMode.FUNDER:
        # Enforce internal-only access.
        require_internal_actor(ctx)
        report = analysis.generate_report_for_funder(document)
    else:
        # Public mode: any role within the tenant can request.
        report = analysis.generate_report_for_public(document)

    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="document_analyzed",
        resource_type="document",
        resource_id=str(document.id),
        actor_role=ctx.role.value,
        metadata={"mode": report.mode.value},
    )
    return report


@router.get(
    "/google/oauth/url",
    response_model=schemas.GoogleOAuthUrlResponse,
    tags=["google", "oauth"],
)
def get_google_oauth_url(
    provider: schemas.GoogleOAuthProvider,
    ctx=Depends(get_request_context),
) -> schemas.GoogleOAuthUrlResponse:
    url = google_oauth.build_authorization_url(
        provider=models.GoogleProvider(provider.value),
        state=str(ctx.tenant_id),
    )
    return schemas.GoogleOAuthUrlResponse(authorization_url=url)


@router.post(
    "/google/oauth/callback",
    tags=["google", "oauth"],
)
async def handle_google_oauth_callback(
    payload: schemas.GoogleOAuthCallbackPayload,
    ctx=Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    cred = await google_oauth.exchange_code_for_tokens(
        code=payload.code,
        provider=models.GoogleProvider(payload.provider.value),
        tenant_id=ctx.tenant_id,
        db=db,
    )
    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="google_oauth_connected",
        resource_type="google",
        resource_id=payload.provider.value,
        actor_role=ctx.role.value,
        metadata=None,
    )
    return {
        "status": "ok",
        "provider": cred.provider.value,
        "tenant_id": cred.tenant_id,
    }


@router.post(
    "/ga/collect",
    tags=["google", "ga"],
)
def collect_ga_metrics(
    payload: schemas.GaCollectRequest,
    ctx=Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    created = ga_gsc.collect_ga_stub(
        db,
        tenant_id=ctx.tenant_id,
        property_id=payload.property_id,
        days=payload.days,
    )
    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="ga_collect",
        resource_type="ga",
        resource_id=payload.property_id,
        actor_role=ctx.role.value,
        metadata={"rows": created},
    )
    return {"rows_created": created}


@router.post(
    "/gsc/collect",
    tags=["google", "gsc"],
)
def collect_gsc_metrics(
    payload: schemas.GscCollectRequest,
    ctx=Depends(get_request_context),
    db: Session = Depends(get_db),
) -> dict:
    created = ga_gsc.collect_gsc_stub(
        db,
        tenant_id=ctx.tenant_id,
        site_url=payload.site_url,
        days=payload.days,
    )
    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="gsc_collect",
        resource_type="gsc",
        resource_id=payload.site_url,
        actor_role=ctx.role.value,
        metadata={"rows": created},
    )
    return {"rows_created": created}


@router.get(
    "/web-impact/summary",
    response_model=schemas.WebImpactSummary,
    tags=["google", "impact"],
)
def get_web_impact_summary(
    days: int = 30,
    ctx=Depends(get_request_context),
    db: Session = Depends(get_db),
) -> schemas.WebImpactSummary:
    summary = ga_gsc.build_web_impact_summary(
        db,
        tenant_id=ctx.tenant_id,
        days=days,
    )
    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="impact_summary_viewed",
        resource_type="impact",
        resource_id=None,
        actor_role=ctx.role.value,
        metadata={"days": days},
    )
    return summary


@router.get(
    "/documents/{document_id}/export",
    response_model=schemas.DocumentExport,
    tags=["documents"],
)
def export_document(
    document_id: int,
    ctx=Depends(get_request_context),
    db: Session = Depends(get_db),
) -> schemas.DocumentExport:
    document = db.get(models.Document, document_id)
    if document is None or document.tenant_id != ctx.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    pages = [
        {"page_number": p.page_number, "text": p.text}
        for p in document.pages
    ]
    fields = [
        {
            "name": f.name.value,
            "value": f.value,
            "page_number": f.page_number,
        }
        for f in document.fields
    ]

    return schemas.DocumentExport(
        document_id=document.id,
        tenant_id=document.tenant_id,
        original_filename=document.original_filename,
        doc_type=schemas.DocumentType(document.doc_type.value),
        pages=pages,
        fields=fields,
    )


@router.delete(
    "/documents/{document_id}",
    tags=["documents"],
)
def delete_document(
    document_id: int,
    ctx=Depends(require_internal_actor),
    db: Session = Depends(get_db),
) -> dict:
    document = db.get(models.Document, document_id)
    if document is None or document.tenant_id != ctx.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found",
        )

    db.delete(document)
    db.commit()

    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="document_deleted",
        resource_type="document",
        resource_id=str(document_id),
        actor_role=ctx.role.value,
        metadata=None,
    )

    return {"status": "deleted"}


@router.post(
    "/maintenance/cleanup",
    tags=["maintenance"],
)
def run_cleanup(
    ctx=Depends(require_internal_actor),
    db: Session = Depends(get_db),
) -> dict:
    deleted = maintenance.cleanup_old_data(db)
    audit.log_event(
        db,
        tenant_id=ctx.tenant_id,
        action="cleanup_run",
        resource_type="maintenance",
        resource_id=None,
        actor_role=ctx.role.value,
        metadata={"deleted": deleted},
    )
    return {"deleted_records": deleted}

