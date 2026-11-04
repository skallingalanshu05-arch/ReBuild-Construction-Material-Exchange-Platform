import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { PlusCircle } from "lucide-react";
import { ResourcePage } from "@/components/common/ResourcePage";
import { useList } from "@/components/common/DataState";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { api, errorMessage } from "@/lib/api";
import { buildRequirementCreatePayload } from "@/lib/backend-map";

export const Route = createFileRoute("/app/requirements")({ component: Page });

function NewRequirement() {
  const qc = useQueryClient();
  const cats = useList<{ id?: string; _id?: string; name: string }>("/categories");
  const [open, setOpen] = useState(false);
  const [f, setF] = useState({ title: "", category_id: "", quantity: "", unit: "tonnes", city: "", needed_by: "" });
  const m = useMutation({
    mutationFn: () => api.post("/requirements", buildRequirementCreatePayload({
      title: f.title,
      category_id: f.category_id,
      quantity: Number(f.quantity),
      unit: f.unit,
      city: f.city,
      needed_by: f.needed_by,
    })),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/requirements/my-requirements"] });
      toast.success("Requirement posted");
      setOpen(false);
    },
    onError: (e) => toast.error(errorMessage(e)),
  });
  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild><Button><PlusCircle /> New requirement</Button></DialogTrigger>
      <DialogContent>
        <DialogHeader><DialogTitle>Post a requirement</DialogTitle></DialogHeader>
        <form className="grid gap-3" onSubmit={(e) => {
          e.preventDefault();
          if (!f.title || !f.category_id || !(Number(f.quantity) > 0) || !f.city || !f.needed_by) {
            return toast.error("Fill in title, category, quantity, city, and needed-by date");
          }
          m.mutate();
        }}>
          <div>
            <Label htmlFor="title">Title</Label>
            <Input id="title" value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} />
          </div>
          <div>
            <Label htmlFor="category_id">Category</Label>
            <select
              id="category_id"
              className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
              value={f.category_id}
              onChange={(e) => setF({ ...f, category_id: e.target.value })}
            >
              <option value="">{cats.isLoading ? "Loading…" : "Select category"}</option>
              {cats.data?.map((c) => (
                <option key={String(c.id ?? c._id)} value={String(c.id ?? c._id)}>{c.name}</option>
              ))}
            </select>
          </div>
          {(["quantity", "unit", "city", "needed_by"] as const).map((k) => (
            <div key={k}>
              <Label htmlFor={k} className="capitalize">{k.replace("_", " ")}</Label>
              <Input id={k} type={k === "quantity" ? "number" : k === "needed_by" ? "date" : "text"} value={f[k]} onChange={(e) => setF({ ...f, [k]: e.target.value })} />
            </div>
          ))}
          <Button type="submit" disabled={m.isPending}>Post</Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}

function Page() {
  return (
    <ResourcePage
      title="My requirements"
      subtitle="Materials your company is looking for."
      endpoint="/requirements/my-requirements"
      columns={[
        { key: "requirement_title", label: "Requirement" },
        { key: "required_quantity", label: "Qty" },
        { key: "unit", label: "Unit" },
        { key: "preferred_location", label: "City" },
        { key: "required_availability_date", label: "Needed by" },
        { key: "requirement_status", label: "Status" },
      ]}
      emptyTitle="No requirements posted"
      emptyHint="Post what you need and we'll surface matching materials."
      action={<NewRequirement />}
    />
  );
}
