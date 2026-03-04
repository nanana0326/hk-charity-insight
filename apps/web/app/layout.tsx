import "./globals.css";
import type { ReactNode } from "react";
import Link from "next/link";
import Image from "next/image";

export const metadata = {
  title: "Foundation for Shared Impact",
  description: "Data & insights platform for Hong Kong charities",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body className="flex min-h-full flex-col bg-white text-gray-900 antialiased">
        <div className="mx-auto flex min-h-screen max-w-6xl flex-1 flex-col px-4 py-4">
          <header className="mb-6 flex items-center justify-between border-b border-[var(--color-border)] pb-4">
            <Link
              href="/"
              className="flex items-center gap-3 no-underline text-gray-900"
            >
              <Image
                src="/fsi-logo.png"
                alt="Foundation for Shared Impact"
                width={48}
                height={48}
                className="rounded-lg object-contain"
              />
              <div>
                <p className="text-lg font-semibold tracking-tight text-gray-900 whitespace-nowrap">
                  Data & insights for charities in Hong Kong
                </p>
                <p className="text-xs text-[var(--color-muted)] whitespace-nowrap">
                  Foundation for Shared Impact
                </p>
              </div>
            </Link>
            <nav className="flex flex-nowrap items-center gap-1 text-xs shrink-0">
              <Link
                href="/faq"
                className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 no-underline transition-colors hover:bg-[var(--color-primary)] hover:text-white"
              >
                FAQ
              </Link>
              <Link
                href="/documents/upload"
                className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 no-underline transition-colors hover:bg-[var(--color-primary)] hover:text-white"
              >
                Documents
              </Link>
              <Link
                href="/impact"
                className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 no-underline transition-colors hover:bg-[var(--color-primary)] hover:text-white"
              >
                Web impact
              </Link>
              <span
                className="h-4 w-px shrink-0 self-center bg-gray-300"
                aria-hidden="true"
              />
              <a
                href="https://funding-ops.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 no-underline transition-colors hover:bg-[var(--color-primary)] hover:text-white"
              >
                Funding Finder
              </a>
              <a
                href="https://sd-alpha-lemon.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 no-underline transition-colors hover:bg-[var(--color-primary)] hover:text-white"
              >
                Charity Finder
              </a>
              <a
                href="https://www.shared-impact.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 no-underline transition-colors hover:bg-[var(--color-primary)] hover:text-white"
              >
                FSI
              </a>
            </nav>
          </header>
          <main className="min-h-0 flex-1">{children}</main>
          <footer className="mt-auto flex flex-wrap items-center justify-center gap-x-6 gap-y-3 border-t border-[var(--color-border)] pt-4 pb-6 text-xs sm:justify-between">
            <div className="flex items-center gap-3">
              <Image
                src="/fsi-logo.png"
                alt=""
                width={40}
                height={40}
                className="rounded-full object-contain"
              />
              <span className="text-gray-500">
                © 2026 Foundation for Shared Impact
              </span>
            </div>
            <div className="flex flex-wrap items-center gap-x-6 gap-y-1">
              <a
                href="https://funding-ops.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-[var(--color-primary)] no-underline hover:underline"
              >
                Funding Finder
              </a>
              <a
                href="https://sd-alpha-lemon.vercel.app/"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-[var(--color-primary)] no-underline hover:underline"
              >
                Charity Finder
              </a>
              <a
                href="https://www.shared-impact.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="font-medium text-[var(--color-primary)] no-underline hover:underline"
              >
                FSI website
              </a>
            </div>
          </footer>
        </div>
      </body>
    </html>
  );
}
