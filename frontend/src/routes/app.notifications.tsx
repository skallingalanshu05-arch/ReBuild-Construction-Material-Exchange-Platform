import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";

export const Route = createFileRoute("/app/notifications")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Notifications"
      endpoint="/notifications"
      columns={[{ key: "title", label: "Notification" }, { key: "message", label: "Details" }, { key: "created_at", label: "Date" }]}
      emptyTitle="Nothing here yet"
    />
  );
}
