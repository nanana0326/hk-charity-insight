import os
import csv
import pathlib
from typing import Tuple

from fastapi import UploadFile
from pypdf import PdfReader
from sqlalchemy.orm import Session
import pytesseract
from pdf2image import convert_from_path

from . import models

# Configure Tesseract and Poppler paths for OCR.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\Users\Lenovo\Downloads\Release-25.12.0-0\poppler-25.12.0\bin"


BASE_STORAGE = pathlib.Path(os.getenv("DOCUMENT_STORAGE_ROOT", "data/uploads"))


def _ensure_storage_root() -> None:
    BASE_STORAGE.mkdir(parents=True, exist_ok=True)


def _save_upload_file(tenant_id: int, upload: UploadFile, document_id: int) -> str:
    _ensure_storage_root()
    tenant_dir = BASE_STORAGE / f"tenant_{tenant_id}" / f"doc_{document_id}"
    tenant_dir.mkdir(parents=True, exist_ok=True)

    extension = pathlib.Path(upload.filename or "").suffix or ".bin"
    dest_path = tenant_dir / f"original{extension}"

    with dest_path.open("wb") as dest:
        while True:
            chunk = upload.file.read(1024 * 1024)
            if not chunk:
                break
            dest.write(chunk)

    return str(dest_path)


def _extract_pages_from_pdf(path: str) -> list[Tuple[int, str]]:
    reader = PdfReader(path)
    pages: list[Tuple[int, str]] = []
    for idx, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        pages.append((idx, text))
    return pages

def _ocr_pages_from_pdf(path: str) -> list[Tuple[int, str]]:
    """Fallback OCR for image-only PDFs."""
    images = convert_from_path(path, poppler_path=POPPLER_PATH)
    pages: list[Tuple[int, str]] = []
    for idx, img in enumerate(images, start=1):
        text = pytesseract.image_to_string(img, lang="eng")
        pages.append((idx, text or ""))
    return pages

def _extract_pages_from_csv(path: str) -> list[Tuple[int, str]]:
    """Read CSV and return as a single page of readable text for analysis."""
    pages: list[Tuple[int, str]] = []
    try:
        with open(path, newline="", encoding="utf-8", errors="replace") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except Exception:
        with open(path, newline="", encoding="utf-16", errors="replace") as f:
            reader = csv.reader(f)
            rows = list(reader)
    if not rows:
        pages.append((1, "(Empty CSV)"))
        return pages
    # Format as readable text: header + rows (limit size for very large CSVs)
    lines = [" | ".join(cell.strip() for cell in row) for row in rows[:2000]]
    text = "\n".join(lines)
    if len(rows) > 2000:
        text += f"\n\n... ({len(rows) - 2000} more rows)"
    pages.append((1, text))
    return pages


def ingest_document(
    db: Session,
    *,
    tenant_id: int,
    user_id: int | None,
    upload: UploadFile,
    doc_type: models.DocumentType = models.DocumentType.OTHER,
) -> tuple[models.Document, bool, int, str | None]:
    """
    Store uploaded file, extract plain text by page (PDF for now),
    and create basic field placeholders.
    """
    document = models.Document(
        tenant_id=tenant_id,
        created_by_user_id=user_id,
        original_filename=upload.filename or "uploaded-document",
        stored_path="",
        mime_type=upload.content_type,
        doc_type=doc_type,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    stored_path = _save_upload_file(tenant_id, upload, document.id)
    document.stored_path = stored_path

    pages: list[tuple[int, str]] = []
    if (upload.content_type or "").lower() in ("application/pdf", "pdf") or stored_path.lower().endswith(
        ".pdf"
    ):
        pages = _extract_pages_from_pdf(stored_path)
        if not any(text.strip() for _, text in pages):
            pages = _ocr_pages_from_pdf(stored_path)
    elif (upload.content_type or "").lower() in (
        "text/csv",
        "application/csv",
        "text-comma-separated-values",
    ) or stored_path.lower().endswith(".csv"):
        pages = _extract_pages_from_csv(stored_path)

    for page_number, text in pages:
        page = models.DocumentPage(
            document_id=document.id,
            page_number=page_number,
            text=text,
        )
        db.add(page)

    db.commit()
    db.refresh(document)

    # Aggregate OCR / text extraction quality.
    total_chars = sum(len(text.strip()) for _, text in pages)
    has_text = total_chars > 0

    preview_chunks = [text.strip() for _, text in pages if text.strip()]
    preview_text = "\n\n".join(preview_chunks)[:800] if preview_chunks else None

    if pages:
        first_page_text = pages[0][1]
        placeholder_fields: list[models.DocumentField] = [
            models.DocumentField(
                document_id=document.id,
                name=models.FieldName.AMOUNT,
                value="TBD – to be extracted by analysis pipeline",
                page_number=None,
            ),
            models.DocumentField(
                document_id=document.id,
                name=models.FieldName.BENEFICIARIES,
                value=first_page_text[:500],
                page_number=1,
            ),
        ]
        for field in placeholder_fields:
            db.add(field)
        db.commit()

    return document, has_text, total_chars, preview_text

