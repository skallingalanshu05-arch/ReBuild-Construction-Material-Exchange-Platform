import { createFileRoute } from "@tanstack/react-router";
import { ResourcePage } from "@/components/common/ResourcePage";

export const Route = createFileRoute("/app/transactions")({ component: Page });

function Page() {
  return (
    <ResourcePage
      title="Transactions"
      endpoint="/transactions"
      columns={[{ key: "material_title", label: "Material" }, { key: "counterparty", label: "Counterparty" }, { key: "quantity", label: "Qty" }, { key: "amount", label: "Amount" }, { key: "status", label: "Status" }, { key: "created_at", label: "Date" }]}
      emptyTitle="Nothing here yet"
    />
  );
}
