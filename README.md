# HK Charity Insights Platform (MVP)

This repository contains an early-stage monorepo for the **HK Charity Insights** platform (Foundation for Shared Impact–oriented document insights and web impact prototypes).

## Current progress (handoff snapshot)

What is already in place:

- **Frontend (`apps/web`)**: Next.js 14 App Router, Tailwind, ECharts; home, FAQ/About, document upload & report views, web impact page with setup guide; email/password auth UI backed by the API.
- **Backend (`apps/api`)**: FastAPI + SQLAlchemy + PostgreSQL; document upload and text extraction for PDF / DOCX / CSV; **LLM-powered** dual-mode reports (funder vs public) via **local Ollama** only (OpenAI-compatible API); audit logging; MVP auth (register/login/password reset hooks); Google OAuth + GA/GSC **stub** collectors and web-impact summary endpoint.
- **Infra**: Docker Compose for Postgres, Redis, MinIO (`infra/`).

What is **not** production-ready or still problematic:

- **PDF image / scanned-document recognition (OCR)** — see below.
- **AI analysis limits** (availability, length cap, output format, quality) — see **AI / LLM analysis**.
- **Forgot-password / password-reset email** — core routes exist but the **product experience for a general-public launch is not finished** — see **Forgot-password — MVP status (why “not fully done”)** below.

## PDF text extraction & OCR — status

- **Selectable-text PDFs** and **Word (.docx)** / **CSV** ingestion paths are the reliable baseline.
- For PDFs where embedded text extraction returns empty content, the code attempts a fallback: **`pdf2image` + Tesseract OCR** (`apps/api/ingest.py`). This path is **fragile and environment-specific**:
  - Tesseract and Poppler paths are currently **hard-coded for one Windows dev machine**; other PCs or Linux/Mac will need configuration changes.
  - OCR quality depends on scan resolution, language, and layout; users may still see **“low quality” / very little text** warnings or unusable analysis — **we have not fully solved image-only PDFs for production.**

Next owner should plan either: configurable paths + documented setup, a hosted OCR service, or clearer UX (“please upload text PDF”) until OCR is solid.

## AI / LLM analysis — status

### What we use

- **Single backend: [Ollama](https://ollama.com/)** running locally (or on a reachable host). The API uses the official **OpenAI-compatible** endpoint (`…/v1`) via the `openai` Python client — see **`apps/api/llm_analysis.py`**, entrypoint **`generate_report_with_ollama`**.
- **Config** comes from **`apps/api/config.py`** / repo-root **`.env`**:
  - **`OLLAMA_BASE_URL`** — default `http://127.0.0.1:11434/v1` (must include `/v1` for the Chat Completions path).
  - **`OLLAMA_MODEL`** — default `llama3.2`; must be a model you have already pulled in Ollama (e.g. `ollama pull llama3.2`).
  - **`OLLAMA_API_KEY`** — placeholder string Ollama accepts; default `ollama`.
- **API surface**: `GET`/`POST` `/api/documents/{id}/analyze?mode=funder|public` loads stored page text, calls the LLM, returns an **`InsightReport`**. There is **no** second cloud provider and **no** Google Gemini in this codebase.

### How it behaves in practice

- The model receives a **fixed English system prompt** (funder vs public “lens”) and the document body as user content. Output is expected as **plain English paragraphs** (not structured JSON).
- The backend concatenates extracted text, then **truncates to ~20,000 characters** before sending. Anything beyond that **never reaches** the model.
- The returned report uses **one main narrative section**; **`charts` is always an empty list** from this path — any dashboard charts on the frontend are not driven by this LLM response today.

### Known issues / risks

| Topic | Detail |
|--------|--------|
| **Availability** | If Ollama is stopped, unreachable, or the model name is wrong, the client fails and the API returns **503**. There is **no** offline or rule-based fallback report. |
| **Ops** | You must keep Ollama running wherever `OLLAMA_BASE_URL` points; CI/staging needs the same or analysis tests will fail. |
| **Global client** | The OpenAI client is created **once** (lazy singleton). Changing env vars at runtime without restarting the API process may not pick up new URLs reliably. |
| **Prompt language** | Instructions are English; mixed Chinese/English **source** documents may still work, but there is **no** explicit bilingual prompt tuning. |
| **Quality & trust** | Text can be vague, wrong on numbers, or miss nuance. Treat as **draft assistive copy**, not compliance-grade or audit-ready analysis; add UX/legal disclaimers if exposing to real charities. |

### Environment variables (AI only)

`OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_API_KEY`

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

### Forgot-password emails (SMTP, Gmail)

1. Copy **`.env.example`** → **`.env`** if needed and fill **`SMTP_USER`**, **`SMTP_PASSWORD`** (Google **App Password**, not your normal Gmail password), **`SMTP_FROM_EMAIL`** (usually same as `SMTP_USER`). Keep **`SMTP_HOST=smtp.gmail.com`**, **`SMTP_PORT=587`**, **`SMTP_USE_TLS=true`**. Template placeholders (`your_email@…`) are ignored until replaced — see **`apps/api/auth.py`**.
2. Gmail: enable **2-Step Verification**, then **Google Account → Security → App passwords** → create one for Mail → paste the 16-character password into **`SMTP_PASSWORD`** (spaces are stripped automatically).
3. Set **`WEB_BASE_URL`** to the exact site URL users open (e.g. `http://localhost:3001` if Next runs on port 3001), so the reset link in the email is correct.
4. Restart **uvicorn** after editing `.env`. If SMTP still fails, check the API terminal log for the full reset link (logged at WARNING) or an exception traceback.

**Public site / many users**

- Visitors **do not** configure SMTP. You set **one** outbound mailbox (or transactional provider) on the **API server**.
- Each reset email goes **to that user's registered address**, sent **from your** configured sender (`SMTP_FROM_EMAIL`). Same flow for any number of users.
- Gmail + App Password is OK for **dev/demo**. For production, prefer **[Google Workspace](https://workspace.google.com/)**, **[Amazon SES](https://aws.amazon.com/ses/)**, **[Resend](https://resend.com/)**, **[SendGrid](https://sendgrid.com/)**, **[Postmark](https://postmarkapp.com/)**, etc., with a domain (`noreply@yourorganisation.org`) and SPF/DKIM so mail does not land in spam.
- Keep SMTP secrets **only** in server-side env (API host / secrets manager), never in the frontend repo or client bundles.

### Forgot-password — MVP status (why it is “not fully done” for public launch)

The **API and UI for requesting and consuming a reset token are implemented** (`/auth/forgot-password`, `/auth/reset-password`, `/api/auth/forgot-password`, `/api/auth/reset-password`). The reason we still treat this area as **incomplete for a broad public website** is:

| Gap | Why it matters |
|-----|----------------|
| **Operations-heavy email delivery** | Reset mail sends **only if** someone configures SMTP + DNS (SPF/DKIM) and **`WEB_BASE_URL`** correctly on the server. Until that is done, users see “check your inbox” but **may receive nothing** (link only in server logs). That is fragile for non-technical visitors. |
| **Plain MVP email** | One English plaintext body — **no** branded HTML template, **no** Chinese/localised copy, **no** dedicated transactional provider integration beyond generic SMTP. |
| **No delivery hardening** | **No** send queue, retries, or bounce handling; failures only appear in API logs. |
| **Abuse / safety limits** | **No** rate limiting or CAPTCHA on forgot-password; suitable risk controls for a spam-facing endpoint are not implemented. |
| **Auth stack is MVP overall** | Sessions use **localStorage + headers**, not production-grade cookies/JWT rotation — acceptable for demos but **not** positioned as finished enterprise identity. |

**Summary:** The **feature is coded**, but **“done for the general public”** requires the **Production checklist** below plus further product/engineering work (templates, i18n, limits, monitoring, stronger auth) depending on your risk tolerance.

### If the browser shows "Failed to fetch" (login, upload, etc.)

Most often the **FastAPI process is not listening** (nothing on port 8000), so the browser cannot reach `/api/...`.

1. **Health check** — open [http://localhost:8000/health](http://localhost:8000/health). If it does not load, start the API (see above). Typical cause: **PostgreSQL is not running** — the app defaults to Postgres on `localhost:5432`; if Docker is off or Postgres is down, startup fails and **no server runs**.
2. **Local dev without Docker / Postgres** — add **`USE_SQLITE_FOR_DEV=true`** to repo-root `.env`. This **forces SQLite** at `data/dev.sqlite`, even if `DATABASE_URL` is still set for Postgres (handy when Docker is off). Restart uvicorn after changing `.env`.
3. **Frontend URL** — `NEXT_PUBLIC_API_BASE_URL` defaults to `http://localhost:8000/api`. Deployed sites must set this to the real API origin + `/api`.
4. **CORS** — `allow_credentials=False` with `allow_origins=["*"]` avoids browser blocking cross-origin `fetch` from `localhost:3000`.

### Start infra services

```bash
cd infra
docker compose up -d
```

This will start PostgreSQL, Redis, and MinIO with development credentials.

### Deploy frontend (Vercel)

- Connect this GitHub repo in Vercel and set **Root Directory** to **`apps/web`** (the `vercel.json` there runs install/build from the monorepo root so `patch-package` can patch hoisted `next`).
- Set **`NEXT_PUBLIC_API_BASE_URL`** to your deployed API origin + `/api` if it is not `localhost`.

### Production checklist (public users — auth links & email)

Use this when the site is **public** (real registrants, forgot-password emails).

| Step | What to do |
|------|------------|
| **1. URLs** | Deploy Next.js to your canonical HTTPS URL (e.g. `https://www.yourorg.hk`). Deploy FastAPI behind **HTTPS** on its own host or path. |
| **2. Frontend env** | Set **`NEXT_PUBLIC_API_BASE_URL`** to **`https://<your-api-host>/api`** (must match where `/health` and `/api/auth/*` live). |
| **3. Backend env — reset links** | Set **`WEB_BASE_URL`** to the **exact** URL users type in the browser for the website (e.g. `https://www.yourorg.hk`). Forgot-password emails build links as `{WEB_BASE_URL}/auth/reset-password?token=…`. Wrong value ⇒ broken links in inbox. |
| **4. Database** | Use **PostgreSQL** in production. **Disable** `USE_SQLITE_FOR_DEV`. Set **`DATABASE_URL`** to your managed Postgres connection string. |
| **5. Transactional email** | Prefer a provider with **SPF/DKIM** guides: [Amazon SES](https://aws.amazon.com/ses/), [Resend](https://resend.com/), [SendGrid](https://sendgrid.com/), [Postmark](https://postmarkapp.com/), or **Google Workspace** SMTP with your domain. Use a sender like **`noreply@yourorg.hk`** (not a random personal Gmail for production brand/trust). |
| **6. SMTP env (API only)** | Set **`SMTP_HOST`**, **`SMTP_PORT`**, **`SMTP_USER`**, **`SMTP_PASSWORD`**, **`SMTP_FROM_EMAIL`**, **`SMTP_USE_TLS`** / **`SMTP_USE_SSL`** per your provider’s docs. Store these **only** on the API host’s secret manager / env UI — never commit real values to Git. |
| **7. DNS** | Add provider-supplied **SPF**, **DKIM**, and ideally **DMARC** records for your sending domain so mail reaches inbox instead of spam. |
| **8. CORS** | For production, narrow **`allow_origins`** in **`apps/api/main.py`** to your real frontend origin(s) instead of `"*"` (recommended once URLs are stable). |
| **9. Smoke test** | Register a throwaway account → Forgot password → confirm email arrives → link opens **`https://www…/auth/reset-password?token=…`** → password updates → login works. |

**Summary:** “Public-ready” forgot-password means **HTTPS + correct `WEB_BASE_URL` / `NEXT_PUBLIC_API_BASE_URL` + production Postgres + domain email with SPF/DKIM**, not extra app code.

## Next steps

- **Stabilise PDF OCR** (config-driven binaries, cross-platform behaviour, or external OCR), and tighten UX when scans fail.
- **Improve AI pipeline**: optional degradation UX when Ollama is down; JSON/schema-guided outputs + charts if needed; handle long documents (chunking or summarisation) beyond the 20k cap.
- Harden **multi-tenant auth** (move beyond header-based MVP / localStorage where appropriate).
- Replace GA/GSC **stub** collectors with real GA4 and Search Console API ingestion.
- Optional: formal DB migrations (Alembic) instead of startup `create_all` + ad-hoc ALTERs for production.

