import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";

export const Route = createFileRoute("/app/impact")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Sustainability impact"
      endpoint="/impact/stats"
      columns={[{ key: "metric", label: "Metric" }, { key: "value", label: "Value" }, { key: "unit", label: "Unit" }]}
      emptyTitle="Nothing here yet"
    />
  );
}
