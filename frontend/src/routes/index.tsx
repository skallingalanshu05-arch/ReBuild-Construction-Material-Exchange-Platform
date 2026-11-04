import { createFileRoute, Link } from "@tanstack/react-router";
import { ArrowRight, Search, Handshake, Truck, Layers, BrickWall, TreePine, Wrench, Zap, PaintBucket, Leaf, BadgeIndianRupee, ShieldCheck, Clock } from "lucide-react";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { Button } from "@/components/ui/button";
import { ListState } from "@/components/common/DataState";
import { MaterialCard, type Material } from "@/components/cards/MaterialCard";
import hero from "@/assets/hero-materials.jpg";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "ReBuild – Give Construction Materials a Second Life" },
      { name: "description", content: "Marketplace connecting construction companies with surplus, reusable building materials." },
      { property: "og:title", content: "ReBuild – Give Construction Materials a Second Life" },
      { property: "og:description", content: "Discover reusable construction materials, reduce waste and build sustainably." },
    ],
  }),
  component: Home,
});

const steps = [
  { icon: Layers, title: "List surplus", text: "Suppliers list leftover or reclaimed materials from their sites." },
  { icon: Search, title: "Get matched", text: "Buyers post requirements and see matches ranked by the platform." },
  { icon: Handshake, title: "Agree terms", text: "Send requests, negotiate and confirm the exchange." },
  { icon: Truck, title: "Reuse", text: "Pick up or deliver — materials get a second life, not a landfill." },
];

const categories = [
  { icon: BrickWall, name: "Bricks & Masonry" },
  { icon: Layers, name: "Steel & Metals" },
  { icon: TreePine, name: "Timber & Wood" },
  { icon: Wrench, name: "Fixtures & Fittings" },
  { icon: Zap, name: "Electrical" },
  { icon: PaintBucket, name: "Finishes" },
];

function Home() {
  return (
    <PublicLayout>
      <section className="relative overflow-hidden">
        <img src={hero} alt="Reclaimed steel beams, timber and bricks at a salvage yard" width={1600} height={1104} className="absolute inset-0 size-full object-cover" />
        <div className="absolute inset-0 bg-hero" />
        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 md:py-36">
          <p className="mb-4 inline-flex items-center gap-2 rounded-full bg-primary-foreground/10 px-3 py-1 text-xs font-medium text-primary-foreground">
            <Leaf className="size-3.5 text-leaf" /> Construction & demolition resource exchange
          </p>
          <h1 className="max-w-2xl text-4xl font-bold leading-tight text-primary-foreground md:text-6xl">
            Give Construction Materials a <span className="text-leaf">Second Life</span>
          </h1>
          <p className="mt-5 max-w-xl text-lg text-primary-foreground/80">
            Connect with construction projects, discover reusable materials, reduce waste and build a more sustainable future.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Button asChild size="lg" variant="leaf">
              <Link to="/materials">Explore Materials <ArrowRight /></Link>
            </Button>
            <Button asChild size="lg" variant="heroOutline">
              <Link to="/register">Register Your Company</Link>
            </Button>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <h2 className="text-3xl font-bold text-primary">How ReBuild works</h2>
        <div className="mt-10 grid gap-6 md:grid-cols-4">
          {steps.map((s, i) => (
            <div key={s.title} className="relative rounded-xl border bg-card p-6 shadow-card">
              <span className="absolute right-5 top-4 font-display text-4xl font-bold text-leaf-soft">0{i + 1}</span>
              <s.icon className="size-7 text-leaf" />
              <h3 className="mt-4 font-semibold">{s.title}</h3>
              <p className="mt-1 text-sm text-muted-foreground">{s.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bg-card py-20">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <h2 className="text-3xl font-bold text-primary">Browse by category</h2>
          <div className="mt-8 grid grid-cols-2 gap-4 md:grid-cols-6">
            {categories.map((c) => (
              <Link key={c.name} to="/materials" search={{ q: c.name }} className="rounded-xl border bg-background p-5 text-center transition hover:border-leaf">
                <c.icon className="mx-auto size-7 text-secondary" />
                <p className="mt-3 text-sm font-medium">{c.name}</p>
              </Link>
            ))}
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <div className="flex items-end justify-between">
          <h2 className="text-3xl font-bold text-primary">Recently listed</h2>
          <Link to="/materials" className="text-sm font-semibold text-secondary hover:underline">View all →</Link>
        </div>
        <div className="mt-8">
          <ListState<Material> endpoint="/materials" params={{ limit: 8, sort: "-created_at" }} emptyTitle="No listings yet" emptyHint="New materials will appear here.">
            {(rows) => (
              <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                {rows.slice(0, 8).map((m, i) => <MaterialCard key={i} m={m} />)}
              </div>
            )}
          </ListState>
        </div>
      </section>

      <section className="bg-primary py-20 text-primary-foreground">
        <div className="mx-auto grid max-w-7xl gap-10 px-4 sm:px-6 md:grid-cols-2">
          {[
            { title: "For buyers", items: [[BadgeIndianRupee, "Source quality materials below new-build cost"], [Search, "Post requirements and get matched automatically"], [Clock, "Find stock near your site, faster"]] },
            { title: "For suppliers", items: [[Leaf, "Turn surplus into revenue instead of disposal cost"], [ShieldCheck, "Deal with verified construction companies"], [Truck, "Clear your sites on schedule"]] },
          ].map((b) => (
            <div key={b.title} className="rounded-2xl bg-primary-foreground/5 p-8">
              <h3 className="text-2xl font-bold">{b.title}</h3>
              <ul className="mt-6 space-y-4">
                {b.items.map(([Icon, t]) => {
                  const I = Icon as typeof Leaf;
                  return (
                    <li key={t as string} className="flex gap-3 text-primary-foreground/85">
                      <I className="size-5 shrink-0 text-leaf" /> {t as string}
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-20 sm:px-6">
        <h2 className="text-3xl font-bold text-primary">Environmental impact</h2>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Live figures for materials reused, waste diverted and CO₂ saved will show here once the platform statistics service is connected. We don't publish estimated numbers.
        </p>
        <div className="mt-8 grid gap-4 md:grid-cols-4">
          {["Materials reused", "Waste diverted", "CO₂ saved", "Companies"].map((k) => (
            <div key={k} className="rounded-xl border bg-card p-6 shadow-card">
              <p className="text-sm text-muted-foreground">{k}</p>
              <p className="mt-2 font-display text-3xl font-bold text-muted-foreground/40">—</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 pb-20 sm:px-6">
        <div className="grid-lines rounded-3xl border bg-leaf-soft/60 p-10 text-center md:p-16">
          <h2 className="text-3xl font-bold text-primary md:text-4xl">Ready to keep materials in use?</h2>
          <p className="mx-auto mt-3 max-w-lg text-muted-foreground">Register your company to list surplus, post requirements and trade with other builders.</p>
          <Button asChild size="lg" className="mt-6">
            <Link to="/register">Get Started</Link>
          </Button>
        </div>
      </section>
    </PublicLayout>
  );
}
