# HK Charity Insights Platform (MVP)

This repository contains an early-stage monorepo for the **HK Charity Insights** platform (Foundation for Shared Impact–oriented document insights and web impact prototypes).

## Current progress (handoff snapshot)

What is already in place:

- **Frontend (`apps/web`)**: Next.js 14 App Router, Tailwind, ECharts; home, FAQ/About, document upload & report views, web impact page with setup guide; email/password auth UI backed by the API.
- **Backend (`apps/api`)**: FastAPI + SQLAlchemy + PostgreSQL; document upload and text extraction for PDF / DOCX / CSV; **LLM-powered** dual-mode reports (funder vs public) via **local Ollama** only (OpenAI-compatible API); audit logging; MVP auth (register/login/password reset hooks); Google OAuth + GA/GSC **stub** collectors and web-impact summary endpoint.
- **Infra**: Docker Compose for Postgres, Redis, MinIO (`infra/`).

What is **not** production-ready or still problematic:

- **PDF image / scanned-document recognition (OCR)** — see below.
- **AI analysis behaviour and naming cleanup** — see **AI / LLM analysis**.

## PDF text extraction & OCR — status

- **Selectable-text PDFs** and **Word (.docx)** / **CSV** ingestion paths are the reliable baseline.
- For PDFs where embedded text extraction returns empty content, the code attempts a fallback: **`pdf2image` + Tesseract OCR** (`apps/api/ingest.py`). This path is **fragile and environment-specific**:
  - Tesseract and Poppler paths are currently **hard-coded for one Windows dev machine**; other PCs or Linux/Mac will need configuration changes.
  - OCR quality depends on scan resolution, language, and layout; users may still see **“low quality” / very little text** warnings or unusable analysis — **we have not fully solved image-only PDFs for production.**

Next owner should plan either: configurable paths + documented setup, a hosted OCR service, or clearer UX (“please upload text PDF”) until OCR is solid.

## AI / LLM analysis — status

**What runs today**

- Document insights come **only from Ollama** via its **OpenAI-compatible** HTTP API — **`apps/api/llm_analysis.py`** (`generate_report_with_ollama`).
- Configure **`apps/api/config.py`** / environment: `OLLAMA_BASE_URL` (default `http://127.0.0.1:11434/v1`), `OLLAMA_MODEL`, `OLLAMA_API_KEY`.

**Known gaps / risks for handoff**

- **No fallback**: If the client cannot start or the API call errors, the route returns **HTTP 503** — there is **no** static or rule-based report fallback.
- **Operational deps**: **Ollama must be running** and the configured model must be pulled locally.
- **Input truncation**: Only the first **~20,000 characters** of extracted document text are sent to the model; very long PDFs may lose tail content from the prompt.
- **Output shape**: The current LLM path returns **plain prose** in one primary section and **`charts=[]`** — structured charts/citations are **not** produced by this generator yet (frontend may expect richer `charts`; verify UX).
- **Quality & compliance**: Outputs can be wrong or incomplete; treat as **draft assistant text**, not audited charity reporting — product/analytical disclaimers may be needed for real NGOs.

**Environment variables** (see also `.env` at repo root)

- `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_API_KEY`

## Structure

- `apps/web` – Next.js (App Router, TypeScript, Tailwind CSS) frontend
- `apps/api` – FastAPI backend
- `infra` – Docker Compose services (PostgreSQL, Redis, MinIO)

## Getting started

### Prerequisites

- Node.js 18+ and npm
- Python 3.11+ and `pip`
- Docker (optional but recommended for local DB/Redis/MinIO)

### Install & run web (Next.js)

```bash
npm install
npm run dev:web
```

Then open `http://localhost:3000`.

### Install & run API (FastAPI)

From the **repository root** (not `apps/api`), so package imports work:

```bash
cd apps/api
pip install -r requirements.txt
cd ../..
python -m uvicorn apps.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Start infra services

```bash
cd infra
docker compose up -d
```

This will start PostgreSQL, Redis, and MinIO with development credentials.

## Next steps

- **Stabilise PDF OCR** (config-driven binaries, cross-platform behaviour, or external OCR), and tighten UX when scans fail.
- **Improve AI pipeline**: optional degradation UX when Ollama is down; JSON/schema-guided outputs + charts if needed; handle long documents (chunking or summarisation) beyond the 20k cap.
- Harden **multi-tenant auth** (move beyond header-based MVP / localStorage where appropriate).
- Replace GA/GSC **stub** collectors with real GA4 and Search Console API ingestion.
- Optional: formal DB migrations (Alembic) instead of startup `create_all` + ad-hoc ALTERs for production.

