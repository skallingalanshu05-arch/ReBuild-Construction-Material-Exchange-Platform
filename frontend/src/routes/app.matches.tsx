import { createFileRoute, Link } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";
import { Progress } from "@/components/ui/progress";

export const Route = createFileRoute("/app/matches")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Smart matches"
      subtitle="Listings ranked against your requirements. Scores come from the matching engine."
      endpoint="/matches"
      columns={[
        { key: "requirement_title", label: "Your requirement" },
        { key: "material_title", label: "Matched material", render: (r) => r.material_id ? <Link to="/materials/$id" params={{ id: String(r.material_id) }} className="font-medium text-secondary hover:underline">{String(r.material_title ?? "View")}</Link> : String(r.material_title ?? "—") },
        { key: "supplier_company", label: "Supplier" },
        { key: "distance_km", label: "Distance (km)" },
        {
          key: "score",
          label: "Match score",
          render: (r) =>
            typeof r.score === "number" ? (
              <div className="flex w-32 items-center gap-2">
                <Progress value={r.score <= 1 ? r.score * 100 : r.score} className="h-2" />
                <span className="text-xs font-semibold">{r.score <= 1 ? Math.round(r.score * 100) : Math.round(r.score)}%</span>
              </div>
            ) : <span className="text-muted-foreground">—</span>,
        },
      ]}
      emptyTitle="No matches yet"
      emptyHint="Post a requirement to start receiving matches."
    />
  );
}
