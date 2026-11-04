import { useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { api, errorMessage } from "@/lib/api";

const ACTION_METHODS: Record<string, "patch" | "post"> = {
  accept: "patch",
  reject: "patch",
  cancel: "patch",
};

/** Shows only actions allowed for the current status. Backend must still enforce the workflow. */
export function RequestActions({ row, role }: { row: Record<string, unknown>; role: "supplier" | "buyer" }) {
  const qc = useQueryClient();
  const id = String(row.id ?? row._id);
  const status = String(row.status ?? row.request_status ?? "").toLowerCase();
  const m = useMutation({
    mutationFn: (action: string) => {
      const method = ACTION_METHODS[action] ?? "patch";
      return api[method](`/requests/${id}/${action}`);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["/requests"] });
      toast.success("Request updated");
    },
    onError: (e) => toast.error(errorMessage(e)),
  });
  if (status !== "pending") return <span className="text-xs text-muted-foreground">—</span>;
  return (
    <div className="flex gap-2">
      {role === "supplier" ? (
        <>
          <Button size="sm" disabled={m.isPending} onClick={() => m.mutate("accept")}>Accept</Button>
          <Button size="sm" variant="outline" disabled={m.isPending} onClick={() => m.mutate("reject")}>Reject</Button>
        </>
      ) : (
        <Button size="sm" variant="outline" disabled={m.isPending} onClick={() => m.mutate("cancel")}>Cancel</Button>
      )}
    </div>
  );
}
