"use client";

import { useEffect, useState } from "react";

import { BaseChart } from "@/components/charts/BaseChart";
import type { InsightReport } from "@/lib/api";
import { fetchFunderReport } from "@/lib/api";

export function DocumentDashboard({ documentId }: { documentId: number }) {
  const [report, setReport] = useState<InsightReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchFunderReport(documentId)
      .then((data) => {
        if (!cancelled) {
          setReport(data);
          setError(null);
        }
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load");
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [documentId]);

  if (loading) {
    return <p className="text-sm text-slate-400">Loading analysis…</p>;
  }

  if (error) {
    return (
      <p className="text-sm text-red-400">
        Failed to load: {error} (please make sure the API is running locally)
      </p>
    );
  }

  if (!report) {
    return <p className="text-sm text-slate-400">No analysis available yet.</p>;
  }

  return (
    <div className="space-y-6">
      <section className="rounded-xl border border-slate-800 bg-slate-900/40 p-5">
        <h2 className="text-lg font-semibold text-slate-50">
          {report.title}
        </h2>
        <p className="mt-2 text-sm text-slate-300">{report.summary}</p>
      </section>

      <section className="grid gap-4 md:grid-cols-3">
        <div className="md:col-span-2 space-y-4">
          {report.sections.map((section) => (
            <article
              key={section.id}
              className="rounded-xl border border-slate-800 bg-slate-900/40 p-4"
            >
              <h3 className="text-sm font-semibold text-slate-100">
                {section.title}
              </h3>
              <p className="mt-2 text-sm text-slate-300">{section.body}</p>
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

