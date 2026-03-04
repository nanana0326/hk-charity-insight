from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserRole(str, Enum):
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class TenantBase(BaseModel):
    name: str


class TenantCreate(TenantBase):
    pass


class TenantRead(TenantBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    email: EmailStr
    display_name: Optional[str] = None
    role: UserRole = UserRole.VIEWER


class UserCreate(UserBase):
    tenant_id: int


class UserRead(UserBase):
    id: int
    tenant_id: int
    is_active: bool

    class Config:
        from_attributes = True


class RequestContext(BaseModel):
    tenant_id: int
    role: UserRole


class DocumentType(str, Enum):
    ANNUAL_REPORT = "annual_report"
    APPLICATION = "application"
    PROJECT_REPORT = "project_report"
    OTHER = "other"


class FieldName(str, Enum):
    AMOUNT = "amount"
    BENEFICIARIES = "beneficiaries"
    THEMES = "themes"
    KPIS = "kpis"
    FUNDING_SOURCES = "funding_sources"
    TIMEFRAME = "timeframe"


class DocumentUploadResponse(BaseModel):
    document_id: int
    pages: int


class DocumentListItem(BaseModel):
    id: int
    original_filename: str
    doc_type: DocumentType
    created_at: str

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: list[DocumentListItem]
class AnalysisMode(str, Enum):
    FUNDER = "funder"
    PUBLIC = "public"


class ChartType(str, Enum):
    PIE = "pie"
    BAR = "bar"
    LINE = "line"
    WORD_CLOUD = "word_cloud"
    TIMELINE = "timeline"


class ChartSpec(BaseModel):
    id: str
    type: ChartType
    title: str
    description: str
    data: dict


class InsightSection(BaseModel):
    id: str
    title: str
    body: str


class InsightCitation(BaseModel):
    field: FieldName
    page_number: int | None = None


class InsightReport(BaseModel):
    mode: AnalysisMode
    document_id: int
    title: str
    summary: str
    sections: list[InsightSection]
    charts: list[ChartSpec]
    citations: list[InsightCitation]


class GoogleOAuthProvider(str, Enum):
    ANALYTICS = "analytics"
    SEARCH_CONSOLE = "search_console"


class GoogleOAuthUrlResponse(BaseModel):
    authorization_url: str


class GoogleOAuthCallbackPayload(BaseModel):
    code: str
    provider: GoogleOAuthProvider


class GaCollectRequest(BaseModel):
    property_id: str
    days: int = 30


class GscCollectRequest(BaseModel):
    site_url: str
    days: int = 30


class WebImpactSummary(BaseModel):
    title: str
    summary: str
    charts: list[ChartSpec]


class DocumentExport(BaseModel):
    document_id: int
    tenant_id: int
    original_filename: str
    doc_type: DocumentType
    pages: list[dict]
    fields: list[dict]


