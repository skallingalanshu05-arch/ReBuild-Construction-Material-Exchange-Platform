import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";
import { RequestActions } from "@/components/common/RequestActions";

export const Route = createFileRoute("/app/requests")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="My requests"
      subtitle="Requests you've sent to suppliers."
      endpoint="/requests"
      params={{ role: "buyer" }}
      columns={[
        { key: "material_id", label: "Material" },
        { key: "supplier_company_id", label: "Supplier" },
        { key: "requested_quantity", label: "Qty" },
        { key: "request_status", label: "Status" },
        { key: "created_at", label: "Sent" },
        { key: "actions", label: "", render: (r) => <RequestActions row={r} role="buyer" /> },
      ]}
      emptyTitle="No requests sent"
      emptyHint="Find a material and send a request to its supplier."
    />
  );
}
