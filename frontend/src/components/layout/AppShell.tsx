import { Link, useNavigate } from "@tanstack/react-router";
import { useState, type ReactNode } from "react";
import {
  LayoutDashboard, Boxes, PlusCircle, ClipboardList, Sparkles, Inbox, Receipt, FolderKanban,
  Bell, MessageSquare, Leaf, UserRound, ShieldCheck, LogOut, Menu,
} from "lucide-react";
import { Logo } from "./Logo";
import { useAuth } from "@/lib/auth";
import { isApiConfigured } from "@/lib/api";
import { Button } from "@/components/ui/button";

const groups = [
  { label: "Overview", items: [["/app", "Dashboard", LayoutDashboard], ["/app/impact", "Impact", Leaf]] },
  { label: "Supplier", items: [["/app/listings", "My listings", Boxes], ["/app/listings/new", "Add material", PlusCircle], ["/app/incoming", "Incoming requests", Inbox]] },
  { label: "Buyer", items: [["/app/requirements", "My requirements", ClipboardList], ["/app/matches", "Smart matches", Sparkles], ["/app/requests", "My requests", Inbox]] },
  { label: "Operations", items: [["/app/transactions", "Transactions", Receipt], ["/app/projects", "Projects", FolderKanban]] },
  { label: "Account", items: [["/app/notifications", "Notifications", Bell], ["/app/messages", "Messages", MessageSquare], ["/app/profile", "Company profile", UserRound]] },
] as const;

export function AppShell({ children }: { children: ReactNode }) {
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);

  const nav = (
    <nav className="space-y-6 px-3 py-6">
      {groups.map((g) => (
        <div key={g.label}>
          <p className="px-3 pb-2 text-[11px] font-semibold uppercase tracking-wider text-sidebar-foreground/50">{g.label}</p>
          {g.items.map(([to, label, Icon]) => (
            <Link
              key={to}
              to={to}
              activeOptions={{ exact: true }}
              onClick={() => setOpen(false)}
              className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-sidebar-foreground hover:bg-sidebar-accent data-[status=active]:bg-sidebar-accent data-[status=active]:text-sidebar-accent-foreground"
            >
              <Icon className="size-4" /> {label}
            </Link>
          ))}
        </div>
      ))}
      {isAdmin && (
        <Link to="/app/admin" className="flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-sidebar-primary hover:bg-sidebar-accent">
          <ShieldCheck className="size-4" /> Admin panel
        </Link>
      )}
    </nav>
  );

  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 hidden h-screen w-64 shrink-0 overflow-y-auto bg-sidebar lg:block">
        <div className="px-6 pt-6"><Logo inverted /></div>
        {nav}
      </aside>
      {open && (
        <div className="fixed inset-0 z-50 lg:hidden" onClick={() => setOpen(false)}>
          <aside className="h-full w-64 overflow-y-auto bg-sidebar" onClick={(e) => e.stopPropagation()}>
            <div className="px-6 pt-6"><Logo inverted /></div>
            {nav}
          </aside>
        </div>
      )}
      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between gap-3 border-b bg-background/90 px-4 backdrop-blur sm:px-8">
          <Button variant="ghost" size="icon" className="lg:hidden" onClick={() => setOpen(true)} aria-label="Open menu"><Menu /></Button>
          <div className="text-sm text-muted-foreground">
            {user ? <>Signed in as <span className="font-semibold text-foreground">{user.full_name ?? user.email}</span></> : "Preview mode"}
          </div>
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" size="icon" aria-label="Notifications"><Link to="/app/notifications"><Bell /></Link></Button>
            {user && (
              <Button variant="outline" size="sm" onClick={async () => { await logout(); navigate({ to: "/login" }); }}>
                <LogOut /> Logout
              </Button>
            )}
          </div>
        </header>
        {!isApiConfigured && (
          <div className="border-b border-warning/40 bg-warning/10 px-4 py-2 text-center text-xs sm:px-8">
            Backend not connected — set <code>VITE_API_BASE_URL</code> to load live data. Screens show which endpoint each section needs.
          </div>
        )}
        <main className="flex-1 px-4 py-8 sm:px-8">{children}</main>
      </div>
    </div>
  );
}

export function PageHeader({ title, subtitle, action }: { title: string; subtitle?: string; action?: ReactNode }) {
  return (
    <div className="mb-8 flex flex-wrap items-end justify-between gap-4">
      <div>
        <h1 className="text-2xl font-bold text-primary md:text-3xl">{title}</h1>
        {subtitle && <p className="mt-1 text-muted-foreground">{subtitle}</p>}
      </div>
      {action}
    </div>
  );
}
