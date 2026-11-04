import { createFileRoute, Outlet, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { AppShell } from "@/components/layout/AppShell";
import { useAuth } from "@/lib/auth";
import { isApiConfigured } from "@/lib/api";

export const Route = createFileRoute("/app")({
  head: () => ({ meta: [{ title: "Dashboard – ReBuild" }, { name: "robots", content: "noindex" }] }),
  component: Layout,
});

function Layout() {
  const { user, ready } = useAuth();
  const navigate = useNavigate();
  // When a backend is configured, the dashboard requires a session.
  // Without one, screens stay viewable in preview mode.
  useEffect(() => {
    if (ready && isApiConfigured && !user) navigate({ to: "/login" });
  }, [ready, user, navigate]);
  if (isApiConfigured && (!ready || !user)) return <div className="grid min-h-screen place-items-center text-muted-foreground">Loading…</div>;
  return (
    <AppShell>
      <Outlet />
    </AppShell>
  );
}
