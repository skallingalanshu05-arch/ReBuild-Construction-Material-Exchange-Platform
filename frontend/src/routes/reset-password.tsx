import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { z } from "zod";
import { toast } from "sonner";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { api, errorMessage } from "@/lib/api";

export const Route = createFileRoute("/reset-password")({
  validateSearch: z.object({ token: z.string().optional() }),
  head: () => ({
    meta: [
      { title: "Reset password – ReBuild" },
      { name: "description", content: "Choose a new password for your ReBuild account." },
      { property: "og:title", content: "Reset password – ReBuild" },
      { property: "og:description", content: "Set a new ReBuild password." },
    ],
  }),
  component: Page,
});

function Page() {
  const { token } = Route.useSearch();
  const navigate = useNavigate();
  const [pw, setPw] = useState("");
  const [pw2, setPw2] = useState("");
  const [busy, setBusy] = useState(false);
  return (
    <AuthLayout title="Set a new password">
      {!token ? (
        <p className="text-sm text-destructive">This reset link is missing its token. Request a new one.</p>
      ) : (
        <form
          className="space-y-4"
          onSubmit={async (e) => {
            e.preventDefault();
            if (pw.length < 8) return toast.error("Password must be at least 8 characters");
            if (pw !== pw2) return toast.error("Passwords don't match");
            setBusy(true);
            try {
              await api.post("/auth/reset-password", { token, new_password: pw });
              toast.success("Password updated — please sign in");
              navigate({ to: "/login" });
            } catch (err) {
              toast.error(errorMessage(err));
            } finally {
              setBusy(false);
            }
          }}
        >
          <div><Label htmlFor="pw">New password</Label><Input id="pw" type="password" value={pw} onChange={(e) => setPw(e.target.value)} /></div>
          <div><Label htmlFor="pw2">Confirm password</Label><Input id="pw2" type="password" value={pw2} onChange={(e) => setPw2(e.target.value)} /></div>
          <Button type="submit" className="w-full" disabled={busy}>Update password</Button>
        </form>
      )}
    </AuthLayout>
  );
}
