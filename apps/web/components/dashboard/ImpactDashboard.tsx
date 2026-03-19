"use client";

import { useEffect, useState } from "react";
import { BaseChart } from "@/components/charts/BaseChart";
import type { WebImpactSummary } from "@/lib/api";
import { fetchWebImpactSummary } from "@/lib/api";

export function ImpactDashboard() {
  const [summary, setSummary] = useState<WebImpactSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetchWebImpactSummary()
      .then((data) => {
        if (!cancelled) {
          setSummary(data);
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
  }, []);

  if (loading) {
    return (
      <p className="text-sm text-[var(--color-muted)]">
        Loading web impact report…
      </p>
    );
  }

  if (error) {
    return (
      <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
        Unable to load web impact data right now. {error}
      </div>
    );
  }

  if (!summary) {
    return (
      <p className="text-sm text-[var(--color-muted)]">
        No web impact data available.
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <section className="grid gap-6 md:grid-cols-2">
        {summary.charts.map((chart) => (
          <BaseChart key={chart.id} spec={chart} />
        ))}
      </section>
    </div>
  );
}
