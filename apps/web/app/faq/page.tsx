import Link from "next/link";

const FAQ_ITEMS = [
  {
    q: "What file formats can I upload?",
    a: "You can upload PDF, Word (.docx), or CSV documents. For best results, use files with selectable text. Scanned PDFs are supported via OCR if Tesseract is installed.",
  },
  {
    q: "What is the difference between Funder and Public view?",
    a: "Funder view focuses on evaluation, risks, sustainability, and fit with funding goals. Public view presents what the organisation does, who it serves, and where the money goes — suitable for donors and media.",
  },
  {
    q: "How long does document analysis take?",
    a: "Small documents usually complete within seconds. Large or multi-page PDFs may take 1–2 minutes. If upload takes longer than 2 minutes, try a smaller file or fewer pages.",
  },
  {
    q: "Why does my document show “No text could be extracted”?",
    a: "This usually means the PDF is image-only (scanned). Upload a PDF with selectable text, or use a Word version. If OCR is enabled on the server, scanned PDFs may still be processed.",
  },
  {
    q: "Where can I find more about Foundation for Shared Impact?",
    a: "Visit the main FSI website for programs, resources, and how to get involved.",
  },
];

export default function FAQPage() {
  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/"
          className="text-sm font-medium text-[var(--color-muted)] transition-colors hover:text-[var(--color-primary)]"
        >
          ← Home
        </Link>
      </div>
      <h1 className="text-3xl font-bold tracking-tight text-gray-900">
        <span className="border-b-4 border-[var(--color-primary)] pb-1">
          FAQ
        </span>
      </h1>
      <section className="space-y-4">
        {FAQ_ITEMS.map((item, i) => (
          <div
            key={i}
            className={`rounded-xl border p-5 shadow-sm ${
              i % 2 === 0
                ? "border-[var(--color-border)] bg-white"
                : "border-orange-200 bg-orange-50/60"
            }`}
          >
            <div className="flex items-start gap-3">
              <span
                className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-[var(--color-primary)] text-sm font-bold text-white"
                aria-hidden
              >
                {i + 1}
              </span>
              <div>
                <h2 className="text-base font-bold text-gray-900 leading-snug">
                  {item.q}
                </h2>
                <p className="mt-2 text-[15px] leading-relaxed text-gray-600">
                  {item.a}
                </p>
              </div>
            </div>
          </div>
        ))}
      </section>
      <p className="rounded-lg bg-gray-100 px-4 py-3 text-sm text-[var(--color-muted)]">
        <a
          href="https://www.shared-impact.com/"
          target="_blank"
          rel="noopener noreferrer"
          className="font-semibold text-[var(--color-primary)] hover:underline"
        >
          Visit FSI website →
        </a>
      </p>
    </div>
  );
}
