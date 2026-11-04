import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";

export const Route = createFileRoute("/app/messages")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Messages"
      endpoint="/messages/conversations"
      columns={[{ key: "participant", label: "With" }, { key: "last_message", label: "Last message" }, { key: "updated_at", label: "Updated" }]}
      emptyTitle="Nothing here yet"
    />
  );
}
