import type { ReactNode } from "react";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

export type Column<T> = { key: string; label: string; render?: (row: T) => ReactNode };

export function fmt(v: unknown): ReactNode {
  if (v == null || v === "") return <span className="text-muted-foreground">—</span>;
  if (typeof v === "boolean") return v ? "Yes" : "No";
  if (typeof v === "object") return JSON.stringify(v);
  const s = String(v);
  if (/^\d{4}-\d{2}-\d{2}T/.test(s)) return new Date(s).toLocaleDateString();
  return s;
}

export function StatusBadge({ value }: { value: unknown }) {
  const s = String(value ?? "").toLowerCase();
  const tone = /accept|approv|active|complete|deliver|available/.test(s)
    ? "bg-leaf-soft text-primary"
    : /reject|cancel|fail|expired/.test(s)
      ? "bg-destructive/10 text-destructive"
      : "bg-concrete text-foreground";
  return <Badge className={`${tone} border-0 capitalize`}>{s.replace(/_/g, " ") || "—"}</Badge>;
}

export function DataTable<T extends Record<string, unknown>>({ rows, columns }: { rows: T[]; columns: Column<T>[] }) {
  return (
    <div className="overflow-x-auto rounded-xl border bg-card shadow-card">
      <Table>
        <TableHeader>
          <TableRow className="bg-muted/60">
            {columns.map((c) => (
              <TableHead key={c.key} className="text-xs font-semibold uppercase tracking-wide">
                {c.label}
              </TableHead>
            ))}
          </TableRow>
        </TableHeader>
        <TableBody>
          {rows.map((r, i) => (
            <TableRow key={String(r.id ?? r._id ?? i)}>
              {columns.map((c) => (
                <TableCell key={c.key}>
                  {c.render ? c.render(r) : c.key === "status" ? <StatusBadge value={r[c.key]} /> : fmt(r[c.key])}
                </TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
