import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";

export const Route = createFileRoute("/app/profile")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Company profile"
      endpoint="/companies/me/members"
      columns={[{ key: "full_name", label: "Member" }, { key: "email", label: "Email" }, { key: "role", label: "Role" }]}
      emptyTitle="Nothing here yet"
    />
  );
}
