import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";

export const Route = createFileRoute("/app/projects")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Projects"
      endpoint="/projects"
      columns={[{ key: "name", label: "Project" }, { key: "city", label: "City" }, { key: "start_date", label: "Start" }, { key: "status", label: "Status" }]}
      emptyTitle="Nothing here yet"
    />
  );
}
