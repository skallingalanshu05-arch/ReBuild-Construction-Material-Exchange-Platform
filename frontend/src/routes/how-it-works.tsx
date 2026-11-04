import { createFileRoute, Link } from "@tanstack/react-router";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { Button } from "@/components/ui/button";

export const Route = createFileRoute("/how-it-works")({
  head: () => ({
    meta: [
      { title: "How It Works – ReBuild" },
      { name: "description", content: "How suppliers and buyers exchange reusable construction materials on ReBuild." },
      { property: "og:title", content: "How It Works – ReBuild" },
      { property: "og:description", content: "List, match, request and reuse construction materials." },
    ],
  }),
  component: Page,
});

const flow = [
  ["Register your company", "Create an account and choose whether you supply, buy, or both."],
  ["List or post a requirement", "Suppliers add surplus materials with quantity, condition and location. Buyers describe what they need."],
  ["Review smart matches", "The platform ranks listings against requirements. Scores come straight from the matching engine."],
  ["Send and manage requests", "Buyers request materials; suppliers accept, reject or negotiate."],
  ["Complete the transaction", "Track pickup or delivery and close out the exchange."],
  ["See your impact", "Follow how much material your company has kept in use."],
];

function Page() {
  return (
    <PublicLayout>
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <h1 className="text-4xl font-bold text-primary">How it works</h1>
        <ol className="mt-10 space-y-6 border-l-2 border-leaf/40 pl-8">
          {flow.map(([t, d], i) => (
            <li key={t} className="relative">
              <span className="absolute -left-[45px] grid size-8 place-items-center rounded-full bg-primary text-sm font-bold text-primary-foreground">{i + 1}</span>
              <h2 className="text-lg font-semibold">{t}</h2>
              <p className="mt-1 text-muted-foreground">{d}</p>
            </li>
          ))}
        </ol>
        <Button asChild size="lg" className="mt-12"><Link to="/register">Register your company</Link></Button>
      </div>
    </PublicLayout>
  );
}
