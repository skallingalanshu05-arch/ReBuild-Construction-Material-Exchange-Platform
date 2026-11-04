import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";

export const Route = createFileRoute("/app/admin")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Admin – companies"
      endpoint="/admin/companies"
      columns={[{ key: "name", label: "Company" }, { key: "city", label: "City" }, { key: "verified", label: "Verified" }, { key: "status", label: "Status" }]}
      emptyTitle="Nothing here yet"
    />
  );
}
