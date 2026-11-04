import { createFileRoute, Link } from "@tanstack/react-router";
import { useQuery, useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { toast } from "sonner";
import { ArrowLeft, MapPin, Boxes } from "lucide-react";
import { PublicLayout } from "@/components/layout/PublicLayout";
import { api, errorMessage, isApiConfigured } from "@/lib/api";
import { useAuth } from "@/lib/auth";
import { NotConnected } from "@/components/common/DataState";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { materialCategory, materialCity, materialName, type Material } from "@/components/cards/MaterialCard";

export const Route = createFileRoute("/materials/$id")({
  head: () => ({
    meta: [
      { title: "Material details – ReBuild" },
      { name: "description", content: "Details, quantity and supplier information for a reusable construction material." },
      { property: "og:title", content: "Material details – ReBuild" },
      { property: "og:description", content: "Reusable construction material listing on ReBuild." },
    ],
  }),
  component: Detail,
});

function Detail() {
  const { id } = Route.useParams();
  const { user } = useAuth();
  const q = useQuery({ queryKey: ["/materials", id], queryFn: async () => (await api.get<Material>(`/materials/${id}`)).data, enabled: isApiConfigured });
  const [qty, setQty] = useState("");
  const [msg, setMsg] = useState("");
  const send = useMutation({
    mutationFn: () => api.post("/requests", { material_id: id, quantity: Number(qty), message: msg }),
    onSuccess: () => {
      toast.success("Request sent to the supplier");
      setQty("");
      setMsg("");
    },
    onError: (e) => toast.error(errorMessage(e)),
  });

  const m = q.data;
  return (
    <PublicLayout>
      <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6">
        <Link to="/materials" className="mb-6 inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-primary">
          <ArrowLeft className="size-4" /> Back to materials
        </Link>
        {!isApiConfigured ? (
          <NotConnected endpoint={`GET /materials/${id}`} />
        ) : q.isLoading ? (
          <Skeleton className="h-96 w-full" />
        ) : q.isError || !m ? (
          <p className="text-destructive">{errorMessage(q.error)}</p>
        ) : (
          <div className="grid gap-10 md:grid-cols-[1.3fr_1fr]">
            <div>
              <div className="aspect-[4/3] overflow-hidden rounded-2xl bg-muted grid-lines">
                {m.images?.[0] ?? m.image_url ? (
                  <img src={(m.images?.[0] ?? m.image_url) as string} alt={materialName(m)} className="size-full object-cover" />
                ) : (
                  <div className="grid size-full place-items-center"><Boxes className="size-14 text-secondary/30" /></div>
                )}
              </div>
              <h1 className="mt-6 text-3xl font-bold text-primary">{materialName(m)}</h1>
              <div className="mt-3 flex flex-wrap gap-2">
                {materialCategory(m) && <Badge className="border-0 bg-leaf-soft text-primary">{materialCategory(m)}</Badge>}
                {m.condition && <Badge variant="outline" className="capitalize">{m.condition}</Badge>}
                {materialCity(m) && <span className="flex items-center gap-1 text-sm text-muted-foreground"><MapPin className="size-4" />{materialCity(m)}</span>}
              </div>
              {m.description && <p className="mt-6 leading-relaxed text-muted-foreground">{m.description}</p>}
            </div>
            <aside className="h-fit rounded-2xl border bg-card p-6 shadow-card">
              <p className="text-sm text-muted-foreground">Available</p>
              <p className="font-display text-3xl font-bold">{m.quantity ?? "—"} <span className="text-lg">{m.unit}</span></p>
              {m.price != null && <p className="mt-1 text-secondary">₹{m.price} / {m.unit ?? "unit"}</p>}
              <div className="mt-6 space-y-3">
                {user ? (
                  <form className="space-y-3" onSubmit={(e) => { e.preventDefault(); if (!qty) return toast.error("Enter a quantity"); send.mutate(); }}>
                    <Input type="number" min={1} placeholder="Quantity needed" value={qty} onChange={(e) => setQty(e.target.value)} aria-label="Quantity" />
                    <Textarea placeholder="Message to supplier" value={msg} onChange={(e) => setMsg(e.target.value)} aria-label="Message" />
                    <Button type="submit" className="w-full" disabled={send.isPending}>{send.isPending ? "Sending…" : "Send request"}</Button>
                  </form>
                ) : (
                  <Button asChild className="w-full"><Link to="/login">Sign in to request this material</Link></Button>
                )}
              </div>
            </aside>
          </div>
        )}
      </div>
    </PublicLayout>
  );
}
