import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";
import { RequestActions } from "@/components/common/RequestActions";

export const Route = createFileRoute("/app/incoming")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Incoming requests"
      subtitle="Buyers asking for your listed materials."
      endpoint="/requests"
      params={{ role: "supplier" }}
      columns={[
        { key: "material_id", label: "Material" },
        { key: "buyer_company_id", label: "Buyer" },
        { key: "requested_quantity", label: "Qty" },
        { key: "message", label: "Message" },
        { key: "request_status", label: "Status" },
        { key: "created_at", label: "Received" },
        { key: "actions", label: "", render: (r) => <RequestActions row={r} role="supplier" /> },
      ]}
      emptyTitle="No incoming requests"
      emptyHint="Requests from buyers will appear here."
    />
  );
}
