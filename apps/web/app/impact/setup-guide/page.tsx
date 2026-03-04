import Link from "next/link";

export const metadata = {
  title: "Web impact setup guide — Foundation for Shared Impact",
  description: "Step-by-step guide to connect Google Analytics and Search Console and collect data for the web impact report.",
};

export default function SetupGuidePage() {
  return (
    <div className="mx-auto max-w-3xl space-y-8 print:max-w-none">
      <div className="flex items-center justify-between rounded-xl border border-[var(--color-border)] bg-[var(--color-primary-light)]/40 p-4 print:border print:bg-gray-100">
        <Link
          href="/impact"
          className="text-sm font-medium text-[var(--color-primary)] hover:underline print:text-gray-700"
        >
          ← Back to Web impact report
        </Link>
        <p className="text-xs text-[var(--color-muted)] print:text-gray-600">
          Print or save as PDF: Ctrl+P (Cmd+P on Mac) → Save as PDF.
        </p>
      </div>

      <header className="border-b border-[var(--color-border)] pb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Web impact report — Setup guide
        </h1>
        <p className="mt-3 text-base text-gray-600 leading-relaxed">
          This guide walks you through connecting your organisation’s Google Analytics and Search Console to the platform so you can generate the web impact report. Five steps: one-time setup, then connect, collect GA, collect GSC, and view the report.
        </p>
      </header>

      {/* Quick overview */}
      <div className="rounded-xl border border-[var(--color-border)] bg-gray-50 p-5">
        <h3 className="text-sm font-semibold text-gray-900 mb-3 uppercase tracking-wide">
          In a nutshell
        </h3>
        <p className="text-sm text-gray-600">
          An admin configures Google OAuth once. Each organisation then authorises the platform (Step 2), after which you trigger data collection for GA and Search Console (Steps 3–4). The report page (Step 5) shows the result. No data yet? Complete Steps 2–4 first.
        </p>
      </div>

      <section className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-bold text-white">1</span>
          <h2 className="text-lg font-semibold text-gray-900">
            Configure Google OAuth <span className="font-normal text-[var(--color-muted)]">(one-time, admin only)</span>
          </h2>
        </div>
        <p className="text-sm text-gray-600 pl-10">
          Before any organisation can connect, the API needs valid Google OAuth credentials. Think of this as turning on the “gate” that lets the platform talk to Google on your behalf.
        </p>
        <div className="pl-10 space-y-3">
          <p className="text-sm text-gray-700">
            <strong>In Google Cloud Console:</strong> Create or pick a project. Enable <strong>Google Analytics Data API</strong> (for GA4) and/or <strong>Webmasters API</strong> (for Search Console).
          </p>
          <p className="text-sm text-gray-700">
            <strong>Create OAuth 2.0 credentials</strong> (Desktop or Web app). Set the authorised redirect URI to match where your backend (or frontend) will receive the callback—e.g. <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">https://your-api-domain/oauth/callback</code>. That’s where Google will send the <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">code</code> after the user signs in.
          </p>
          <p className="text-sm text-gray-700">
            On the server running the API, set: <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">GOOGLE_CLIENT_ID</code>, <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">GOOGLE_CLIENT_SECRET</code>, <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">GOOGLE_REDIRECT_URI</code>.
          </p>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-bold text-white">2</span>
          <h2 className="text-lg font-semibold text-gray-900">
            Connect your organisation to Google
          </h2>
        </div>
        <p className="text-sm text-gray-600 pl-10">
          Someone with admin or analyst rights does this once per organisation. You’re basically saying: “This Google account is allowed to share GA and/or Search Console data with the platform.”
        </p>

        <div className="pl-10 space-y-4">
          <div className="rounded-lg border border-[var(--color-border)] bg-white p-4">
            <p className="text-sm font-semibold text-gray-900 mb-2">Step A — Get the authorisation URL</p>
            <p className="text-sm text-gray-700 mb-2">
              Call the API with your tenant headers (<code className="bg-gray-100 px-1 rounded text-xs">X-Tenant-Id</code>, <code className="bg-gray-100 px-1 rounded text-xs">X-User-Role</code>):
            </p>
            <p className="text-xs font-mono text-gray-800 bg-gray-50 p-3 rounded border border-gray-200 break-all">
              GET /api/google/oauth/url?provider=analytics<br />
              GET /api/google/oauth/url?provider=search_console
            </p>
            <p className="text-sm text-gray-600 mt-2">
              The response contains <code className="bg-gray-100 px-1 rounded text-xs">authorization_url</code>. You will open this in the next step.
            </p>
          </div>

          <div className="rounded-lg border border-[var(--color-border)] bg-white p-4">
            <p className="text-sm font-semibold text-gray-900 mb-2">Step B — Sign in with Google</p>
            <p className="text-sm text-gray-700">
              Open the <code className="bg-gray-100 px-1 rounded text-xs">authorization_url</code> in a browser. Sign in with the Google account that has access to the GA4 property and/or Search Console site you want to use. After you approve, Google will redirect back to your app with a <code className="bg-gray-100 px-1 rounded text-xs">code</code> in the URL.
            </p>
          </div>

          <div className="rounded-lg border border-[var(--color-border)] bg-white p-4">
            <p className="text-sm font-semibold text-gray-900 mb-2">Step C — Send the code to the API</p>
            <p className="text-sm text-gray-700 mb-2">
              Take the <code className="bg-gray-100 px-1 rounded text-xs">code</code> from the redirect URL and call:
            </p>
            <p className="text-xs font-mono text-gray-800 bg-gray-50 p-3 rounded border border-gray-200 break-all">
              POST /api/google/oauth/callback<br />
              Body: {`{ "code": "<code from URL>", "provider": "analytics" }`}<br />
              or <code className="bg-gray-100 px-1 rounded">"search_console"</code> if you connected Search Console.
            </p>
            <p className="text-sm text-gray-600 mt-2">
              The API stores the tokens for your tenant. You can then run the collect steps (3 and 4).
            </p>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-bold text-white">3</span>
          <h2 className="text-lg font-semibold text-gray-900">
            Collect Google Analytics data
          </h2>
        </div>
        <p className="text-sm text-gray-600 pl-10">
          Now you pull GA4 metrics for a time range. You need the <strong>property ID</strong>—the numeric ID of your GA4 property (GA4 Admin → Property settings).
        </p>
        <div className="pl-10 rounded-lg border border-[var(--color-border)] bg-white p-4">
          <p className="text-sm text-gray-700">
            <strong>Request:</strong> <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">POST /api/ga/collect</code> with body <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">{`{ "property_id": "123456789", "days": 30 }`}</code>. Same tenant headers as before.
          </p>
          <p className="mt-2 text-xs text-[var(--color-muted)]">
            Only works if Step 2 was done for <code className="bg-gray-100 px-1 rounded">provider=analytics</code>. The API then collects (or in the MVP, generates placeholder) sessions, users, pageviews per day. Response includes <code className="bg-gray-100 px-1 rounded">rows_created</code>.
          </p>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-bold text-white">4</span>
          <h2 className="text-lg font-semibold text-gray-900">
            Collect Search Console data
          </h2>
        </div>
        <p className="text-sm text-gray-600 pl-10">
          Same idea as GA, but for Search Console. The <strong>site URL</strong> must match exactly what you see in Search Console—e.g. <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">https://www.example.org/</code> or <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">sc_domain:example.org</code>.
        </p>
        <div className="pl-10 rounded-lg border border-[var(--color-border)] bg-white p-4">
          <p className="text-sm text-gray-700">
            <strong>Request:</strong> <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">POST /api/gsc/collect</code> with body <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">{`{ "site_url": "https://www.your-site.org/", "days": 30 }`}</code>.
          </p>
          <p className="mt-2 text-xs text-[var(--color-muted)]">
            Again, Step 2 must be done for <code className="bg-gray-100 px-1 rounded">provider=search_console</code>. The API then pulls (or in the MVP, generates placeholder) clicks, impressions, CTR, position per day.
          </p>
        </div>
      </section>

      <section className="space-y-4">
        <div className="flex items-baseline gap-2">
          <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-bold text-white">5</span>
          <h2 className="text-lg font-semibold text-gray-900">
            View the web impact report
          </h2>
        </div>
        <p className="text-sm text-gray-600 pl-10">
          Open the Web impact report page in the platform. It calls <code className="bg-gray-100 px-1.5 py-0.5 rounded text-xs">GET /api/web-impact/summary?days=30</code> and shows the overview and charts. If you see “No web impact data available”, go back and finish Steps 2–4 for your organisation.
        </p>
      </section>

      <footer className="pt-6 border-t border-[var(--color-border)] text-xs text-[var(--color-muted)]">
        Foundation for Shared Impact — Web impact setup guide. Print or save as PDF for offline use.
      </footer>
    </div>
  );
}
