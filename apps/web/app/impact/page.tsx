import { ImpactDashboard } from "@/components/dashboard/ImpactDashboard";

export default function ImpactPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold text-gray-900">Web impact report</h2>
      <p className="text-sm text-[var(--color-muted)]">
        Traffic and search performance from Google Analytics and Search Console.
        The current view shows session and search click trends.
      </p>

      <section className="rounded-2xl border border-[var(--color-border)] bg-gray-50 p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-2">
          How the web impact report works
        </h3>
        <ol className="list-decimal list-inside space-y-2 text-sm text-gray-600">
          <li>
            <strong>Connect Google</strong> — Your organisation authorises the platform to read Google Analytics and/or Google Search Console (via Google OAuth). This is done once per organisation; the API stores the connection securely.
          </li>
          <li>
            <strong>Collect data</strong> — The platform pulls metrics (e.g. sessions, users, pageviews from GA; clicks, impressions, CTR from Search Console) for a chosen period (e.g. last 30 or 90 days). Right now this is triggered via the API (see below); a “Refresh data” button can be added on this page later.
          </li>
          <li>
            <strong>View the report</strong> — This page shows an overview built from that data: session trends, search click trends, and a short summary. Future versions can add top pages, traffic sources, and search keyword opportunities.
          </li>
        </ol>
        <p className="mt-4 text-sm text-[var(--color-muted)]">
          For detailed instructions on connecting Google and collecting data,{" "}
          <a
            href="/impact/setup-guide"
            className="font-medium text-[var(--color-primary)] hover:underline"
          >
            see the step-by-step setup guide
          </a>{" "}
          (you can print that page or save it as PDF).
        </p>
      </section>

      <ImpactDashboard />
    </div>
  );
}
