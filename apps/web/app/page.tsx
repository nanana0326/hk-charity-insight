"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { fetchDocumentList } from "@/lib/api";

type DocumentListItem = {
  id: number;
  original_filename: string;
  doc_type: string;
  created_at: string;
};

function DocIcon() {
  return (
    <svg className="w-10 h-10 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  );
}

function ChartIcon() {
  return (
    <svg className="w-10 h-10 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
  );
}

export default function HomePage() {
  const [documents, setDocuments] = useState<DocumentListItem[]>([]);
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

  return (
    <div className="space-y-8">
      <section className="rounded-2xl border border-[var(--color-border)] bg-gradient-to-br from-orange-100 via-orange-50/80 to-sky-100 p-6 shadow-lg">
        <h2 className="text-xl font-semibold text-[var(--color-primary)]">
          Welcome to Foundation for Shared Impact
        </h2>
        <p className="mt-3 text-sm text-gray-700">
          This platform helps charities and funders work with document analysis and web impact insights.
          Upload annual reports, funding applications, or project reports and view tailored analysis
          from a <strong>funder</strong> perspective (risks, fit, sustainability) or a <strong>public</strong> perspective
          (what we do, who we serve, where the money goes).
        </p>
        <p className="mt-3 text-sm text-gray-700">
          Foundation for Shared Impact connects different sectors to facilitate collaboration and sharing
          of resources, knowledge, and information to drive systems change and build resilient communities.
        </p>
        <p className="mt-4 text-sm">
          <a
            href="https://www.shared-impact.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-[var(--color-primary)] underline decoration-2 underline-offset-2 hover:no-underline"
          >
            Visit FSI website →
          </a>
        </p>
      </section>

      <section className="grid gap-6 md:grid-cols-2">
        <Link
          href="/documents/upload"
          className="group flex gap-4 rounded-2xl border-2 border-[var(--color-border)] bg-white p-6 no-underline text-gray-900 shadow-sm transition-all hover:border-[var(--color-primary)] hover:shadow-md"
        >
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-[var(--color-primary-light)]">
            <DocIcon />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 group-hover:text-[var(--color-primary)] transition-colors">
              Document analysis
            </h3>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              Upload annual reports, funding applications, or project reports.
              Then view insights tailored for <strong>funders</strong> (risks, fit, sustainability)
              or for the <strong>public</strong> (what we do, who we serve, where the money goes).
            </p>
            <span className="mt-3 inline-block text-sm font-medium text-[var(--color-primary)]">
              Upload a document →
            </span>
          </div>
        </Link>

        <Link
          href="/impact"
          className="group flex gap-4 rounded-2xl border-2 border-[var(--color-border)] bg-white p-6 no-underline text-gray-900 shadow-sm transition-all hover:border-[var(--color-primary)] hover:shadow-md"
        >
          <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-xl bg-[var(--color-primary-light)]">
            <ChartIcon />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 group-hover:text-[var(--color-primary)] transition-colors">
              Web traffic analysis
            </h3>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              Connect your organisation’s Google Analytics and Search Console
              to generate a web impact report: traffic trends, top pages, and search performance.
            </p>
            <span className="mt-3 inline-block text-sm font-medium text-[var(--color-primary)]">
              View web impact →
            </span>
          </div>
        </Link>
      </section>

      <section className="rounded-2xl border border-[var(--color-border)] bg-white px-4 py-3 shadow-sm flex items-center justify-between gap-4">
        <div>
          <h3 className="text-sm font-semibold text-gray-900">Your documents</h3>
          <p className="mt-0.5 text-xs text-[var(--color-muted)]">
            {listLoading
              ? "Loading…"
              : listError
              ? "Documents could not be loaded."
              : documents.length === 0
              ? "No documents yet. Upload a document to get started."
              : `${documents.length} document${documents.length > 1 ? "s" : ""} uploaded.`}
          </p>
        </div>
        <Link
          href="/documents/upload"
          className="whitespace-nowrap rounded-full border border-[var(--color-border)] bg-[var(--color-primary-light)] px-3 py-1.5 text-xs font-medium text-[var(--color-primary)] no-underline hover:bg-orange-100"
        >
          View documents →
        </Link>
      </section>
    </div>
  );
}
