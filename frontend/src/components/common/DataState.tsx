import { useQuery } from "@tanstack/react-query";
import { PlugZap, AlertTriangle, PackageOpen, RotateCw } from "lucide-react";
import type { ReactNode } from "react";
import { api, ApiNotConfiguredError, asList, errorMessage, isApiConfigured } from "@/lib/api";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";

export function NotConnected({ endpoint }: { endpoint: string }) {
  return (
    <div className="rounded-xl border border-dashed border-leaf/50 bg-leaf-soft/40 p-8 text-center">
      <PlugZap className="mx-auto mb-3 size-8 text-secondary" />
      <p className="font-display font-semibold text-primary">Waiting for the backend</p>
      <p className="mt-1 text-sm text-muted-foreground">
        This section loads from <code className="rounded bg-card px-1.5 py-0.5 text-xs">{endpoint}</code> once
        VITE_API_BASE_URL is set.
      </p>
    </div>
  );
}

export function EmptyState({ title, hint, action }: { title: string; hint?: string; action?: ReactNode }) {
  return (
    <div className="rounded-xl border bg-card p-10 text-center shadow-card">
      <PackageOpen className="mx-auto mb-3 size-8 text-leaf" />
      <p className="font-display font-semibold">{title}</p>
      {hint && <p className="mt-1 text-sm text-muted-foreground">{hint}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function useList<T = Record<string, unknown>>(endpoint: string, params?: Record<string, unknown>) {
  return useQuery({
    queryKey: [endpoint, params],
    queryFn: async () => asList<T>((await api.get(endpoint, { params })).data),
    enabled: isApiConfigured,
    retry: (n, e) => !(e instanceof ApiNotConfiguredError) && n < 1,
  });
}

export function ListState<T>({
  endpoint,
  params,
  emptyTitle,
  emptyHint,
  emptyAction,
  children,
}: {
  endpoint: string;
  params?: Record<string, unknown>;
  emptyTitle: string;
  emptyHint?: string;
  emptyAction?: ReactNode;
  children: (rows: T[]) => ReactNode;
}) {
  const q = useList<T>(endpoint, params);
  if (!isApiConfigured) return <NotConnected endpoint={`GET ${endpoint}`} />;
  if (q.isLoading)
    return (
      <div className="space-y-3">
        {[0, 1, 2].map((i) => (
          <Skeleton key={i} className="h-14 w-full" />
        ))}
      </div>
    );
  if (q.isError)
    return (
      <div className="rounded-xl border border-destructive/30 bg-card p-8 text-center">
        <AlertTriangle className="mx-auto mb-3 size-7 text-destructive" />
        <p className="font-semibold">Couldn't load this section</p>
        <p className="mt-1 text-sm text-muted-foreground">{errorMessage(q.error)}</p>
        <Button variant="outline" size="sm" className="mt-4" onClick={() => q.refetch()}>
          <RotateCw /> Try again
        </Button>
      </div>
    );
  if (!q.data?.length) return <EmptyState title={emptyTitle} hint={emptyHint} action={emptyAction} />;
  return <>{children(q.data)}</>;
}
