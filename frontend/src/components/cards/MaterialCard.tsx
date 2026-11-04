import { Link } from "@tanstack/react-router";
import { MapPin, Boxes } from "lucide-react";
import { Badge } from "@/components/ui/badge";

export type Material = {
  id?: string;
  _id?: string;
  title?: string;
  name?: string;
  category?: string | { name?: string };
  quantity?: number;
  unit?: string;
  condition?: string;
  price?: number;
  location?: string | { city?: string };
  city?: string;
  images?: string[];
  image_url?: string;
  status?: string;
  description?: string;
  [k: string]: unknown;
};

export const materialId = (m: Material) => String(m.id ?? m._id ?? "");
export const materialName = (m: Material) => m.title ?? m.name ?? "Untitled material";
export const materialCategory = (m: Material) => (typeof m.category === "object" ? m.category?.name : m.category);
export const materialCity = (m: Material) => (typeof m.location === "object" ? m.location?.city : m.location) ?? m.city;

export function MaterialCard({ m }: { m: Material }) {
  const img = m.images?.[0] ?? m.image_url;
  return (
    <Link
      to="/materials/$id"
      params={{ id: materialId(m) }}
      className="group overflow-hidden rounded-xl border bg-card shadow-card transition hover:-translate-y-0.5"
    >
      <div className="aspect-[4/3] bg-muted grid-lines">
        {img ? (
          <img src={img} alt={materialName(m)} loading="lazy" className="size-full object-cover" />
        ) : (
          <div className="grid size-full place-items-center">
            <Boxes className="size-10 text-secondary/40" />
          </div>
        )}
      </div>
      <div className="space-y-2 p-4">
        <div className="flex items-center justify-between gap-2">
          {materialCategory(m) && <Badge className="border-0 bg-leaf-soft text-primary">{materialCategory(m)}</Badge>}
          {m.condition && <span className="text-xs capitalize text-muted-foreground">{m.condition}</span>}
        </div>
        <h3 className="font-semibold group-hover:text-secondary">{materialName(m)}</h3>
        <div className="flex items-center justify-between text-sm text-muted-foreground">
          <span>
            {m.quantity ?? "—"} {m.unit ?? ""}
          </span>
          {materialCity(m) && (
            <span className="flex items-center gap-1">
              <MapPin className="size-3.5" /> {materialCity(m)}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
