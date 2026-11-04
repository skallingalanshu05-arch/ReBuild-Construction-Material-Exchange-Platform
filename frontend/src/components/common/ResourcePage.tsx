import type { ReactNode } from "react";
import { PageHeader } from "@/components/layout/AppShell";
import { ListState } from "./DataState";
import { DataTable, type Column } from "./DataTable";

type Row = Record<string, unknown>;

export function ResourcePage({
  title,
  subtitle,
  endpoint,
  params,
  columns,
  emptyTitle,
  emptyHint,
  action,
}: {
  title: string;
  subtitle?: string;
  endpoint: string;
  params?: Record<string, unknown>;
  columns: Column<Row>[];
  emptyTitle: string;
  emptyHint?: string;
  action?: ReactNode;
}) {
  return (
    <>
      <PageHeader title={title} subtitle={subtitle} action={action} />
      <ListState<Row> endpoint={endpoint} params={params} emptyTitle={emptyTitle} emptyHint={emptyHint} emptyAction={action}>
        {(rows) => <DataTable rows={rows} columns={columns} />}
      </ListState>
    </>
  );
}
