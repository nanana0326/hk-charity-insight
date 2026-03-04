# HK Charity Insights Platform (MVP)

This repository contains an early-stage monorepo for the **HK Charity Insights** platform.

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

```bash
cd apps/api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### Start infra services

```bash
cd infra
docker compose up -d
```

This will start PostgreSQL, Redis, and MinIO with development credentials.

## Next steps

- Implement multi-tenant auth and role-based access.
- Build the document ingestion and analysis pipeline.
- Integrate GA4 and Search Console OAuth and data collection.

