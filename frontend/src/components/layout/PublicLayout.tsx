import { Link } from "@tanstack/react-router";
import type { ReactNode } from "react";
import { Button } from "@/components/ui/button";
import { Logo } from "./Logo";
import { useAuth } from "@/lib/auth";

const nav = [
  { to: "/", label: "Home" },
  { to: "/materials", label: "Explore Materials" },
  { to: "/how-it-works", label: "How It Works" },
  { to: "/about", label: "About Us" },
] as const;

export function PublicLayout({ children }: { children: ReactNode }) {
  const { user } = useAuth();
  return (
    <div className="flex min-h-screen flex-col">
      <header className="sticky top-0 z-40 border-b bg-background/85 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
          <Logo />
          <nav className="hidden items-center gap-1 md:flex">
            {nav.map((n) => (
              <Link
                key={n.to}
                to={n.to}
                activeOptions={{ exact: n.to === "/" }}
                className="rounded-md px-3 py-2 text-sm font-medium text-muted-foreground hover:text-primary data-[status=active]:text-primary"
              >
                {n.label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            {user ? (
              <Button asChild>
                <Link to="/app">Dashboard</Link>
              </Button>
            ) : (
              <>
                <Button asChild variant="ghost" className="hidden sm:inline-flex">
                  <Link to="/login">Login</Link>
                </Button>
                <Button asChild>
                  <Link to="/register">Get Started</Link>
                </Button>
              </>
            )}
          </div>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-4 pb-2 md:hidden">
          {nav.map((n) => (
            <Link key={n.to} to={n.to} className="whitespace-nowrap rounded-md px-3 py-1.5 text-sm text-muted-foreground">
              {n.label}
            </Link>
          ))}
        </nav>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="bg-primary text-primary-foreground">
        <div className="mx-auto grid max-w-7xl gap-8 px-4 py-12 sm:px-6 md:grid-cols-4">
          <div className="md:col-span-2">
            <Logo inverted />
            <p className="mt-3 max-w-sm text-sm text-primary-foreground/70">
              Give construction materials a second life. A resource exchange for surplus and reclaimed building materials.
            </p>
          </div>
          <div className="space-y-2 text-sm">
            <p className="font-semibold">Platform</p>
            <Link to="/materials" className="block text-primary-foreground/70 hover:text-primary-foreground">Explore materials</Link>
            <Link to="/how-it-works" className="block text-primary-foreground/70 hover:text-primary-foreground">How it works</Link>
          </div>
          <div className="space-y-2 text-sm">
            <p className="font-semibold">Company</p>
            <Link to="/about" className="block text-primary-foreground/70 hover:text-primary-foreground">About us</Link>
            <Link to="/register" className="block text-primary-foreground/70 hover:text-primary-foreground">Register your company</Link>
          </div>
        </div>
        <div className="border-t border-primary-foreground/10 py-4 text-center text-xs text-primary-foreground/60">
          © {new Date().getFullYear()} ReBuild
        </div>
      </footer>
    </div>
  );
}
