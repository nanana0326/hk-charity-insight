import Link from "next/link";

export default function AboutPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/"
          className="text-sm text-[var(--color-muted)] hover:text-[var(--color-primary)]"
        >
          ← Home
        </Link>
      </div>
      <h1 className="text-2xl font-semibold text-gray-900">About</h1>
      <section className="rounded-2xl border border-[var(--color-border)] bg-white p-6 shadow-sm">
        <h2 className="text-lg font-semibold text-gray-900">
          Data & insights for charities in Hong Kong
        </h2>
        <p className="mt-3 text-sm text-gray-600">
          This platform helps charities and funders work with document analysis and web impact insights.
          Upload annual reports, funding applications, or project reports and view tailored analysis
          from a <strong>funder</strong> perspective (risks, fit, sustainability) or a <strong>public</strong> perspective
          (what we do, who we serve, where the money goes).
        </p>
        <p className="mt-3 text-sm text-gray-600">
          Foundation for Shared Impact connects different sectors to facilitate collaboration and sharing
          of resources, knowledge, and information to drive systems change and build resilient communities.
        </p>
        <p className="mt-4 text-sm">
          <a
            href="https://www.shared-impact.com/"
            target="_blank"
            rel="noopener noreferrer"
            className="font-medium text-[var(--color-primary)] hover:underline"
          >
            Visit FSI website →
          </a>
        </p>
      </section>
    </div>
  );
}
