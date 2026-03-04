import { redirect, notFound } from "next/navigation";

interface PageProps {
  params: { id: string };
}

export default function DocumentDashboardRedirect({ params }: PageProps) {
  const id = Number(params.id);
  if (!Number.isFinite(id) || id <= 0) notFound();
  redirect(`/documents/${id}`);
}
