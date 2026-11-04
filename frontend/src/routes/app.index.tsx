import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { Boxes, ClipboardList, Inbox, Receipt, PlusCircle } from "lucide-react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { PageHeader } from "@/components/layout/AppShell";
import { NotConnected } from "@/components/common/DataState";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { api, errorMessage, isApiConfigured } from "@/lib/api";

export const Route = createFileRoute("/app/")({ component: Dashboard });

type Summary = {
  active_listings?: number;
  open_requirements?: number;
  pending_requests?: number;
  completed_transactions?: number;
  monthly?: { month: string; listings?: number; transactions?: number }[];
};

const cards = [
  ["active_listings", "Active listings", Boxes],
  ["open_requirements", "Open requirements", ClipboardList],
  ["pending_requests", "Pending requests", Inbox],
  ["completed_transactions", "Completed transactions", Receipt],
] as const;

function Dashboard() {
  // ASSUMED endpoint: GET /dashboard/summary
  const q = useQuery({ queryKey: ["/dashboard/summary"], queryFn: async () => (await api.get<Summary>("/dashboard/summary")).data, enabled: isApiConfigured });
  return (
    <>
      <PageHeader
        title="Dashboard"
        subtitle="Your exchange activity at a glance."
        action={<Button asChild><Link to="/app/listings/new"><PlusCircle /> Add material</Link></Button>}
      />
      {!isApiConfigured ? (
        <NotConnected endpoint="GET /dashboard/summary" />
      ) : q.isError ? (
        <p className="text-destructive">{errorMessage(q.error)}</p>
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
            {cards.map(([k, label, Icon]) => (
              <div key={k} className="rounded-xl border bg-card p-5 shadow-card">
                <div className="flex items-center justify-between text-sm text-muted-foreground">{label}<Icon className="size-4 text-leaf" /></div>
                {q.isLoading ? <Skeleton className="mt-3 h-8 w-16" /> : <p className="mt-2 font-display text-3xl font-bold">{q.data?.[k] ?? "—"}</p>}
              </div>
            ))}
          </div>
          {!!q.data?.monthly?.length && (
            <div className="mt-6 rounded-xl border bg-card p-5 shadow-card">
              <p className="mb-4 font-semibold">Monthly activity</p>
              <div className="h-72">
                <ResponsiveContainer>
                  <BarChart data={q.data.monthly}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                    <XAxis dataKey="month" fontSize={12} />
                    <YAxis fontSize={12} />
                    <Tooltip />
                    <Bar dataKey="listings" fill="var(--chart-1)" radius={[6, 6, 0, 0]} />
                    <Bar dataKey="transactions" fill="var(--chart-2)" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}
        </>
      )}
    </>
  );
}
