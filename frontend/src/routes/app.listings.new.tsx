import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { PageHeader } from "@/components/layout/AppShell";
import { FieldError } from "@/components/layout/AuthLayout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useList } from "@/components/common/DataState";
import { api, errorMessage, tokenStore } from "@/lib/api";
import { buildMaterialCreatePayload } from "@/lib/backend-map";

export const Route = createFileRoute("/app/listings/new")({ component: Page });

const schema = z.object({
  title: z.string().trim().min(3, "Enter a title").max(120),
  category_id: z.string().min(1, "Choose a category"),
  quantity: z.coerce.number().positive("Must be more than 0"),
  unit: z.string().trim().min(1, "Required"),
  condition: z.enum(["new", "like_new", "good", "fair"]),
  price: z.coerce.number().min(0).optional(),
  city: z.string().trim().min(2, "Required"),
  available_from: z.string().optional(),
  description: z.string().trim().max(2000).optional(),
});
type V = z.infer<typeof schema>;

function Page() {
  const navigate = useNavigate();
  const qc = useQueryClient();
  const cats = useList<{ id?: string; _id?: string; name: string }>("/categories");
  const { register, handleSubmit, formState } = useForm<V>({ resolver: zodResolver(schema), defaultValues: { condition: "good" } });
  const onSubmit = handleSubmit(async (v) => {
    try {
      await api.post("/materials", buildMaterialCreatePayload(v));
      qc.invalidateQueries({ queryKey: ["/materials/my-listings"] });
      toast.success("Material listed");
      navigate({ to: "/app/listings" });
    } catch (e) {
      toast.error(errorMessage(e));
    }
  });
  const e = formState.errors;
  return (
    <>
      <PageHeader title="Add material" subtitle="Describe the surplus material you want to list." />
      <form onSubmit={onSubmit} className="grid max-w-3xl gap-5 rounded-xl border bg-card p-6 shadow-card sm:grid-cols-2">
        <div className="sm:col-span-2"><Label htmlFor="title">Title</Label><Input id="title" placeholder="e.g. Reclaimed I-section steel beams" {...register("title")} /><FieldError msg={e.title?.message} /></div>
        <div>
          <Label htmlFor="category_id">Category</Label>
          <select id="category_id" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm" {...register("category_id")}>
            <option value="">{cats.isLoading ? "Loading…" : cats.data?.length ? "Select" : "No categories available"}</option>
            {cats.data?.map((c) => <option key={String(c.id ?? c._id)} value={String(c.id ?? c._id)}>{c.name}</option>)}
          </select>
          <FieldError msg={e.category_id?.message} />
        </div>
        <div>
          <Label htmlFor="condition">Condition</Label>
          <select id="condition" className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm" {...register("condition")}>
            <option value="new">New / unused</option><option value="like_new">Like new</option><option value="good">Good</option><option value="fair">Fair</option>
          </select>
        </div>
        <div><Label htmlFor="quantity">Quantity</Label><Input id="quantity" type="number" step="any" {...register("quantity")} /><FieldError msg={e.quantity?.message} /></div>
        <div><Label htmlFor="unit">Unit</Label><Input id="unit" placeholder="tonnes, pieces, m³" {...register("unit")} /><FieldError msg={e.unit?.message} /></div>
        <div><Label htmlFor="price">Price per unit (₹, optional)</Label><Input id="price" type="number" step="any" {...register("price")} /></div>
        <div><Label htmlFor="city">City</Label><Input id="city" {...register("city")} /><FieldError msg={e.city?.message} /></div>
        <div><Label htmlFor="available_from">Available from</Label><Input id="available_from" type="date" {...register("available_from")} /></div>
        <div className="sm:col-span-2"><Label htmlFor="description">Description</Label><Textarea id="description" rows={4} {...register("description")} /></div>
        <div className="flex gap-3 sm:col-span-2">
          <Button type="submit" disabled={formState.isSubmitting}>{formState.isSubmitting ? "Saving…" : "Publish listing"}</Button>
          <Button type="button" variant="outline" onClick={() => navigate({ to: "/app/listings" })}>Cancel</Button>
        </div>
      </form>
    </>
  );
}
