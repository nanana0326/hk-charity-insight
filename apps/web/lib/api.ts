export type ChartType =
  | "pie"
  | "bar"
  | "line"
  | "word_cloud"
  | "timeline";

export interface ChartSpec {
  id: string;
  type: ChartType;
  title: string;
  description: string;
  data: Record<string, unknown>;
}

export interface InsightSection {
  id: string;
  title: string;
  body: string;
}

export interface InsightReport {
  mode: "funder" | "public";
  document_id: number;
  title: string;
  summary: string;
  sections: InsightSection[];
  charts: ChartSpec[];
}

export interface DocumentListItem {
  id: number;
  original_filename: string;
  doc_type: string;
  created_at: string;
}

export interface DocumentListResponse {
  documents: DocumentListItem[];
}

export interface WebImpactSummary {
  title: string;
  summary: string;
  charts: ChartSpec[];
}

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

const defaultHeaders = {
  "X-Tenant-Id": "1",
  "X-User-Role": "admin",
};

export async function fetchDocumentList(): Promise<DocumentListResponse> {
  const res = await fetch(`${API_BASE}/documents`, { headers: defaultHeaders });
  if (!res.ok) throw new Error(`Failed to list documents: ${res.statusText}`);
  return (await res.json()) as DocumentListResponse;
}

export async function fetchReport(
  documentId: number,
  mode: "funder" | "public"
): Promise<InsightReport> {
  const res = await fetch(
    `${API_BASE}/documents/${documentId}/analyze?mode=${mode}`,
    { headers: defaultHeaders }
  );
  if (!res.ok) throw new Error(`Failed to fetch report: ${res.statusText}`);
  return (await res.json()) as InsightReport;
}

export async function uploadDocument(
  file: File,
  docType: string = "other"
): Promise<{ document_id: number; pages: number }> {
  const form = new FormData();
  form.append("file", file);
  form.append("doc_type", docType);

  const res = await fetch(`${API_BASE}/documents/upload`, {
    method: "POST",
    headers: { ...defaultHeaders } as Record<string, string>,
    body: form,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error((err as { detail?: string }).detail ?? res.statusText);
  }
  return (await res.json()) as { document_id: number; pages: number };
}

export async function fetchFunderReport(documentId: number): Promise<InsightReport> {
  return fetchReport(documentId, "funder");
}

export async function fetchWebImpactSummary(
  days: number = 30
): Promise<WebImpactSummary> {
  const url = new URL(`${API_BASE}/web-impact/summary`);
  url.searchParams.set("days", String(days));
  const res = await fetch(url.toString(), { headers: defaultHeaders });
  if (!res.ok) throw new Error(`Failed to fetch impact summary: ${res.statusText}`);
  return (await res.json()) as WebImpactSummary;
}
