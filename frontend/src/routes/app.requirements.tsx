import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { PlusCircle } from "lucide-react";
import { ResourcePage } from "@/components/common/ResourcePage";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { api, errorMessage } from "@/lib/api";

export const Route = createFileRoute("/app/requirements")({ component: Page });

function NewRequirement() {
  const qc = useQueryClient();
  const [open, setOpen] = useState(false);
  const [f, setF] = useState({ title: "", quantity: "", unit: "", city: "", needed_by: "" });
  const m = useMutation({
    mutationFn: () => api.post("/requirements", { ...f, quantity: Number(f.quantity) }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/requirements/mine"] });
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
        <form className="grid gap-3" onSubmit={(e) => { e.preventDefault(); if (!f.title || !(Number(f.quantity) > 0)) return toast.error("Enter a title and quantity"); m.mutate(); }}>
          {(["title", "quantity", "unit", "city", "needed_by"] as const).map((k) => (
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
      endpoint="/requirements/mine"
      columns={[
        { key: "title", label: "Requirement" },
        { key: "quantity", label: "Qty" },
        { key: "unit", label: "Unit" },
        { key: "city", label: "City" },
        { key: "needed_by", label: "Needed by" },
        { key: "status", label: "Status" },
      ]}
      emptyTitle="No requirements posted"
      emptyHint="Post what you need and we'll surface matching materials."
      action={<NewRequirement />}
    />
  );
}
