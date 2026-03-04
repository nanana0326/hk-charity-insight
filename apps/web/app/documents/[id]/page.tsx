import { notFound } from "next/navigation";
import Link from "next/link";

interface PageProps {
  params: { id: string };
}

export default function DocumentDetailPage({ params }: PageProps) {
  const id = Number(params.id);
  if (!Number.isFinite(id) || id <= 0) notFound();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/documents"
          className="text-sm text-[var(--color-muted)] hover:text-[var(--color-primary)]"
        >
          ← Back to documents
        </Link>
      </div>

      <h2 className="text-xl font-semibold text-gray-900">Choose analysis perspective</h2>
      <p className="text-sm text-[var(--color-muted)]">
        After uploading a document, you can view insights in two ways: one for <strong>funders</strong> (evaluation, risks, fit)
        and one for the <strong>public</strong> (what we do, who we serve, where the money goes).
      </p>

      <div className="grid gap-6 md:grid-cols-2">
        <Link
          href={`/documents/${id}/funder`}
          className="group flex flex-col rounded-2xl border-2 border-[var(--color-border)] bg-white p-6 no-underline text-gray-900 shadow-sm transition-all hover:border-[var(--color-primary)] hover:shadow-md"
        >
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--color-primary-light)]">
            <svg className="h-6 w-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
          <h3 className="font-semibold text-gray-900 group-hover:text-[var(--color-primary)] transition-colors">
            Funder / internal mode
          </h3>
          <p className="mt-2 flex-1 text-sm text-[var(--color-muted)]">
            Evaluation and decision support: funding flow anomalies, project sustainability,
            risks and opportunities, and fit with your funding goals.
          </p>
          <span className="mt-4 text-sm font-medium text-[var(--color-primary)]">
            View funder analysis →
          </span>
        </Link>

        <Link
          href={`/documents/${id}/public`}
          className="group flex flex-col rounded-2xl border-2 border-[var(--color-border)] bg-white p-6 no-underline text-gray-900 shadow-sm transition-all hover:border-[var(--color-primary)] hover:shadow-md"
        >
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-[var(--color-primary-light)]">
            <svg className="h-6 w-6 text-[var(--color-primary)]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
          </div>
          <h3 className="font-semibold text-gray-900 group-hover:text-[var(--color-primary)] transition-colors">
            Public overview mode
          </h3>
          <p className="mt-2 flex-1 text-sm text-[var(--color-muted)]">
            Clear, shareable summary: what the organisation does, who it serves,
            how well it’s doing, and where the money goes — for donors, volunteers, and media.
          </p>
          <span className="mt-4 text-sm font-medium text-[var(--color-primary)]">
            View public overview →
          </span>
        </Link>
      </div>
    </div>
  );
}
