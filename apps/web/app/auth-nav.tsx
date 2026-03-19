"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

function hasAuthInStorage() {
  if (typeof window === "undefined") return false;
  return Boolean(window.localStorage.getItem("auth"));
}

export default function AuthNav() {
  const pathname = usePathname();
  const router = useRouter();
  const [isAuthed, setIsAuthed] = useState(false);

  useEffect(() => {
    setIsAuthed(hasAuthInStorage());
  }, [pathname]);

  function handleLogout() {
    if (typeof window !== "undefined") {
      window.localStorage.removeItem("auth");
      window.dispatchEvent(new Event("auth-changed"));
    }
    setIsAuthed(false);
    router.push("/");
    router.refresh();
  }

  if (!isAuthed) {
    return (
      <Link
        href="/auth/sign-in"
        className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 no-underline transition-colors hover:bg-[var(--color-primary)] hover:text-white"
      >
        Sign in
      </Link>
    );
  }

  return (
    <button
      type="button"
      onClick={handleLogout}
      className="whitespace-nowrap rounded-full px-3 py-1.5 font-medium text-gray-700 transition-colors hover:bg-[var(--color-primary)] hover:text-white"
    >
      Log out
    </button>
  );
}
