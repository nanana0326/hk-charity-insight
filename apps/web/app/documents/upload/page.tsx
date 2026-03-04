"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { uploadDocument, fetchDocumentList } from "@/lib/api";

const DOC_TYPES = [
  { value: "annual_report", label: "Annual report" },
  { value: "application", label: "Funding application" },
  { value: "project_report", label: "Project report" },
  { value: "other", label: "Other" },
] as const;

const VIEW_AS = [
  {
    value: "funder",
    label: "Funder / internal",
    description: "Evaluation, risks, sustainability, fit with funding goals",
  },
  {
    value: "public",
    label: "Public",
    description: "What we do, who we serve, where the money goes — for donors & media",
  },
] as const;

function DocIcon() {
  return (
    <svg className="w-5 h-5 text-[var(--color-muted)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

export default function UploadPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [docType, setDocType] = useState<string>("other");
  const [viewAs, setViewAs] = useState<"funder" | "public">("funder");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [documents, setDocuments] = useState<{ id: number; original_filename: string; doc_type: string; created_at: string }[]>([]);
  const [listLoading, setListLoading] = useState(true);
  const [listError, setListError] = useState(false);

  useEffect(() => {
    fetchDocumentList()
      .then((r) => {
        setDocuments(r.documents);
        setListError(false);
      })
      .catch(() => setListError(true))
      .finally(() => setListLoading(false));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      setError("Please select a file.");
      return;
    }
    setError(null);
    setUploading(true);
    try {
      const result = await uploadDocument(file, docType);
      router.push(`/documents/${result.document_id}/${viewAs}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed.";
      const friendlyMessage =
        message === "Failed to fetch"
          ? "Could not reach the analysis service. Make sure the API is running. From the project root run: python -m uvicorn apps.api.main:app --reload --host 0.0.0.0"
          : message;
      setError(friendlyMessage);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <div className="flex items-center gap-4">
        <Link
          href="/"
          className="text-sm text-[var(--color-muted)] hover:text-[var(--color-primary)]"
        >
          ← Home
        </Link>
      </div>
      <h2 className="text-xl font-semibold text-gray-900">Upload a document</h2>
      <p className="text-sm text-[var(--color-muted)]">
        Upload an annual report, funding application, or project report (PDF, Word, or CSV).
        Choose whether to view the analysis from a <strong>funder</strong> or <strong>public</strong> perspective.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6 rounded-2xl border border-[var(--color-border)] bg-white p-6 shadow-sm">
        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            {error}
          </p>
        )}

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            View this report as
          </label>
          <p className="mb-3 text-xs text-[var(--color-muted)]">
            Choose the perspective for the analysis you want to see first. You can switch to the other view later from the document page.
          </p>
          <div className="space-y-3">
            {VIEW_AS.map((opt) => (
              <label
                key={opt.value}
                className={`flex cursor-pointer items-start gap-3 rounded-xl border-2 p-4 transition-colors ${
                  viewAs === opt.value
                    ? "border-[var(--color-primary)] bg-[var(--color-primary-light)]/40"
                    : "border-[var(--color-border)] bg-white hover:border-gray-300"
                }`}
              >
                <input
                  type="radio"
                  name="viewAs"
                  value={opt.value}
                  checked={viewAs === opt.value}
                  onChange={() => setViewAs(opt.value as "funder" | "public")}
                  className="mt-1 h-4 w-4 border-gray-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]"
                />
                <div>
                  <span className="font-medium text-gray-900">{opt.label}</span>
                  <p className="mt-0.5 text-sm text-[var(--color-muted)]">
                    {opt.description}
                  </p>
                </div>
              </label>
            ))}
          </div>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            Document type
          </label>
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-gray-900 focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
          >
            {DOC_TYPES.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-gray-700">
            File (PDF, Word, or CSV)
          </label>
          <div className="flex flex-wrap items-center gap-3 rounded-lg border border-gray-200 bg-white px-4 py-3">
            <label className="cursor-pointer rounded-lg border-0 bg-[var(--color-primary-light)] px-4 py-2 text-sm font-medium text-[var(--color-primary)] transition-colors hover:bg-orange-100">
              Upload a file
              <input
                type="file"
                accept=".pdf,.docx,.csv,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/csv,application/csv"
                onChange={(e) => setFile(e.target.files?.[0] ?? null)}
                className="sr-only"
              />
            </label>
            <span className="text-sm text-gray-600">
              {file ? file.name : "No file selected"}
            </span>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={uploading || !file}
            className="rounded-xl bg-[var(--color-primary)] px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-[var(--color-primary-hover)] disabled:opacity-50 disabled:pointer-events-none"
          >
            {uploading ? "Uploading…" : "Upload"}
          </button>
          <Link
            href="/"
            className="rounded-xl border border-[var(--color-border)] bg-white px-4 py-2.5 text-sm font-medium text-gray-700 no-underline transition-colors hover:bg-gray-50"
          >
            Cancel
          </Link>
        </div>
      </form>

      <section>
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Your documents</h3>
        {listLoading && (
          <p className="text-sm text-[var(--color-muted)]">Loading…</p>
        )}
        {!listLoading && listError && (
          <p className="text-sm text-[var(--color-muted)]">Documents could not be loaded. Upload above to add a new one.</p>
        )}
        {!listLoading && !listError && documents.length === 0 && (
          <p className="text-sm text-[var(--color-muted)]">No documents yet. Upload one above.</p>
        )}
        {!listLoading && !listError && documents.length > 0 && (
          <ul className="space-y-2">
            {documents.map((doc) => (
              <li key={doc.id}>
                <Link
                  href={`/documents/${doc.id}`}
                  className="flex items-center gap-3 rounded-lg border border-[var(--color-border)] bg-white p-3 no-underline text-gray-900 transition-colors hover:border-[var(--color-primary)] hover:bg-[var(--color-primary-light)]/20"
                >
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-[var(--color-primary-light)]">
                    <DocIcon />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-sm truncate">{doc.original_filename}</p>
                    <p className="text-xs text-[var(--color-muted)]">
                      {doc.doc_type.replace("_", " ")} · {doc.created_at.slice(0, 10)}
                    </p>
                  </div>
                  <span className="text-xs text-[var(--color-primary)]">View →</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
