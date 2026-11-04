import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { Search } from "lucide-react";
import { z } from "zod";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ListState } from "@/components/common/DataState";
import { MaterialCard, type Material } from "@/components/cards/MaterialCard";

export const Route = createFileRoute("/materials/")({
  validateSearch: z.object({ q: z.string().optional(), city: z.string().optional(), condition: z.string().optional() }),
  head: () => ({
    meta: [
      { title: "Explore Materials – ReBuild" },
      { name: "description", content: "Browse reusable and surplus construction materials listed by builders near you." },
      { property: "og:title", content: "Explore Materials – ReBuild" },
      { property: "og:description", content: "Browse reusable and surplus construction materials." },
    ],
  }),
  component: Explore,
});

function Explore() {
  const search = Route.useSearch();
  const navigate = useNavigate({ from: "/materials/" });
  const [q, setQ] = useState(search.q ?? "");
  const [city, setCity] = useState(search.city ?? "");
  const [condition, setCondition] = useState(search.condition ?? "");

  return (
    <PublicLayout>
      <div className="border-b bg-card">
        <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
          <h1 className="text-3xl font-bold text-primary">Explore materials</h1>
          <p className="mt-1 text-muted-foreground">Active listings from construction companies. Sign in to contact suppliers.</p>
          <form
            className="mt-6 grid gap-3 md:grid-cols-[1fr_200px_200px_auto]"
            onSubmit={(e) => {
              e.preventDefault();
              navigate({ search: { q: q || undefined, city: city || undefined, condition: condition || undefined } });
            }}
          >
            <div className="relative">
              <Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
              <Input className="pl-9" placeholder="Search steel, bricks, timber…" value={q} onChange={(e) => setQ(e.target.value)} aria-label="Search" />
            </div>
            <Input placeholder="City" value={city} onChange={(e) => setCity(e.target.value)} aria-label="City" />
            <select
              aria-label="Condition"
              value={condition}
              onChange={(e) => setCondition(e.target.value)}
              className="h-9 rounded-md border border-input bg-background px-3 text-sm"
            >
              <option value="">Any condition</option>
              <option value="new">New / unused</option>
              <option value="like_new">Like new</option>
              <option value="good">Good</option>
              <option value="fair">Fair</option>
            </select>
            <Button type="submit">Search</Button>
          </form>
        </div>
      </div>
      <div className="mx-auto max-w-7xl px-4 py-10 sm:px-6">
        <ListState<Material>
          endpoint="/materials"
          params={{ q: search.q, city: search.city, condition: search.condition }}
          emptyTitle="No materials match"
          emptyHint="Try a broader search or another city."
        >
          {(rows) => (
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
              {rows.map((m, i) => <MaterialCard key={i} m={m} />)}
            </div>
          )}
        </ListState>
      </div>
    </PublicLayout>
  );
}
