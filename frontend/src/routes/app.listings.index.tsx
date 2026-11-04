import { createFileRoute, Link } from "@tanstack/react-router";
import { PlusCircle } from "lucide-react";
import { ResourcePage } from "@/components/common/ResourcePage";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/app/listings/")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="My listings"
      subtitle="Materials your company has listed."
      endpoint="/materials/my-listings"
      columns={[
        { key: "title", label: "Material", render: (r) => <Link to="/materials/$id" params={{ id: String(r.id ?? r._id) }} className="font-medium text-secondary hover:underline">{String(r.title ?? r.name ?? "—")}</Link> },
        { key: "category", label: "Category", render: (r) => String((r.category as { name?: string })?.name ?? r.category ?? "—") },
        { key: "quantity", label: "Qty" },
        { key: "unit", label: "Unit" },
        { key: "condition", label: "Condition" },
        { key: "status", label: "Status" },
        { key: "created_at", label: "Listed" },
      ]}
      emptyTitle="No listings yet"
      emptyHint="List your first surplus material."
      action={<Button asChild><Link to="/app/listings/new"><PlusCircle /> Add material</Link></Button>}
    />
  );
}
