import { notFound } from "next/navigation";
import Link from "next/link";
import { DocumentReportView } from "@/components/dashboard/DocumentReportView";

interface PageProps {
  params: { id: string };
}

export default function DocumentPublicPage({ params }: PageProps) {
  const id = Number(params.id);
  if (!Number.isFinite(id) || id <= 0) notFound();

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href={`/documents/${id}`}
          className="text-sm text-[var(--color-muted)] hover:text-[var(--color-primary)]"
        >
          ← Back to document
        </Link>
      </div>
      <h2 className="text-xl font-semibold text-gray-900">
        Public overview
      </h2>
      <p className="text-sm text-[var(--color-muted)]">
        What the organisation does, who it serves, how well it’s doing, and where the money goes.
      </p>
      <DocumentReportView documentId={id} mode="public" />
    </div>
  );
}
