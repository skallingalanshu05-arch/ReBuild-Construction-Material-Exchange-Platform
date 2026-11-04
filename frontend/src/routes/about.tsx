import { createFileRoute } from "@tanstack/react-router";
import { PublicLayout } from "@/components/layout/PublicLayout";

export const Route = createFileRoute("/about")({
  head: () => ({
    meta: [
      { title: "About Us – ReBuild" },
      { name: "description", content: "ReBuild helps the construction industry keep usable materials out of landfill." },
      { property: "og:title", content: "About ReBuild" },
      { property: "og:description", content: "Our mission: give construction materials a second life." },
    ],
  }),
  component: Page,
});

function Page() {
  return (
    <PublicLayout>
      <div className="mx-auto max-w-3xl px-4 py-16 sm:px-6">
        <p className="text-sm font-semibold uppercase tracking-wider text-leaf">About us</p>
        <h1 className="mt-2 text-4xl font-bold text-primary">Building less waste into every project</h1>
        <div className="mt-8 space-y-5 text-lg leading-relaxed text-muted-foreground">
          <p>Construction and demolition produce huge volumes of material that is still perfectly usable — surplus bricks, offcut steel, reclaimed timber, unused fittings. Most of it is never reused simply because the right buyer never hears about it.</p>
          <p>ReBuild is a resource exchange that connects the companies who have these materials with the companies who need them, making reuse as easy as ordering new.</p>
        </div>
      </div>
    </PublicLayout>
  );
}
