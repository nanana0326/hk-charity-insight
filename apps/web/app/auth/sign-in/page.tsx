"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000/api";

export default function SignInPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!email || !password) {
      setError("Please enter both email and password.");
      return;
    }
    setError(null);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email,
          password,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error((err as { detail?: string }).detail ?? res.statusText);
      }
      const user = (await res.json()) as {
        id: number;
        tenant_id: number;
        role: string;
        email: string;
        display_name?: string | null;
      };

      // Persist simple auth info for subsequent API calls.
      if (typeof window !== "undefined") {
        window.localStorage.setItem(
          "auth",
          JSON.stringify({
            userId: user.id,
            tenantId: user.tenant_id,
            role: user.role,
            email: user.email,
          })
        );
        window.dispatchEvent(new Event("auth-changed"));
      }

      router.push("/");
    } catch (err) {
      const message = err instanceof Error ? err.message : "Sign-in failed.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-md space-y-6">
      <h1 className="text-xl font-semibold text-gray-900">Log in</h1>
      <p className="text-sm text-[var(--color-muted)]">
        Log in with your email and password to see and manage your own uploaded documents.
      </p>
      <form
        onSubmit={handleSubmit}
        className="space-y-4 rounded-2xl border border-[var(--color-border)] bg-white p-6 shadow-sm"
      >
        {error && (
          <p className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-800">
            {error}
          </p>
        )}
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Email
          </label>
          <input
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-sm text-gray-900 focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            placeholder="you@example.org"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-[var(--color-border)] bg-white px-3 py-2 text-sm text-gray-900 focus:border-[var(--color-primary)] focus:outline-none focus:ring-1 focus:ring-[var(--color-primary)]"
            placeholder="Enter your password"
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full rounded-xl bg-[var(--color-primary)] px-4 py-2.5 text-sm font-medium text-white shadow-sm transition-colors hover:bg-[var(--color-primary-hover)] disabled:opacity-50"
        >
          {loading ? "Logging in…" : "Log in"}
        </button>
      </form>
      <div className="flex items-center justify-between text-xs text-[var(--color-muted)]">
        <a
          href="/auth/register"
          className="font-medium text-[var(--color-primary)] no-underline hover:underline"
        >
          Create an account
        </a>
        <a
          href="/auth/forgot-password"
          className="font-medium text-[var(--color-primary)] no-underline hover:underline"
        >
          Forgot password?
        </a>
      </div>
    </div>
  );
}

