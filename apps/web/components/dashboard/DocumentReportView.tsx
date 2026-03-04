"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { BaseChart } from "@/components/charts/BaseChart";
import type { InsightReport } from "@/lib/api";
import { fetchReport } from "@/lib/api";

type Mode = "funder" | "public";

export function DocumentReportView({
  documentId,
  mode,
}: {
  documentId: number;
  mode: Mode;
}) {
  const [report, setReport] = useState<InsightReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchReport(documentId, mode)
      .then((data) => {
        if (!cancelled) {
          setReport(data);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled)
          setError(err instanceof Error ? err.message : "Failed to load");
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [documentId, mode]);

  if (loading) {
    return (
      <p className="text-sm text-[var(--color-muted)]">Loading analysis…</p>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        Failed to load: {error}. Make sure the API is running and you have access (funder mode requires admin/analyst role).
      </div>
    );
  }

  if (!report) {
    return (
      <p className="text-sm text-[var(--color-muted)]">No analysis available.</p>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-2xl border border-[var(--color-border)] bg-[var(--color-primary-light)]/30 p-6">
        <h2 className="text-lg font-semibold text-gray-900">{report.title}</h2>
        <p className="mt-2 text-sm text-gray-600">{report.summary}</p>
      </section>

      <section className="grid gap-6 md:grid-cols-3">
        <div className="md:col-span-2 space-y-4">
          {report.sections.map((section) => (
            <article
              key={section.id}
              className="rounded-xl border border-[var(--color-border)] bg-white p-5 shadow-sm"
            >
              <h3 className="text-sm font-semibold text-gray-900">
                {section.title}
              </h3>
              <p className="mt-2 text-sm text-gray-600">{section.body}</p>
            </article>
          ))}
        </div>
        <div className="space-y-4">
          {report.charts.map((chart) => (
            <BaseChart key={chart.id} spec={chart} />
          ))}
        </div>
      </section>
    </div>
  );
}
