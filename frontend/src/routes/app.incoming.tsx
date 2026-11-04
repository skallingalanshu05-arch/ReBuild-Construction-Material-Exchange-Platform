import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";
import { RequestActions } from "@/components/common/RequestActions";

export const Route = createFileRoute("/app/incoming")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Incoming requests"
      subtitle="Buyers asking for your listed materials."
      endpoint="/requests/incoming"
      columns={[
        { key: "material_title", label: "Material" },
        { key: "buyer_company", label: "Buyer" },
        { key: "quantity", label: "Qty" },
        { key: "message", label: "Message" },
        { key: "status", label: "Status" },
        { key: "created_at", label: "Received" },
        { key: "actions", label: "", render: (r) => <RequestActions row={r} role="supplier" /> },
      ]}
      emptyTitle="No incoming requests"
      emptyHint="Requests from buyers will appear here."
    />
  );
}
