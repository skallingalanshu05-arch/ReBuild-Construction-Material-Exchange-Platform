import { createFileRoute, Link } from "@tanstack/react-router";
import { useState } from "react";
import { toast } from "sonner";
import { AuthLayout } from "@/components/layout/AuthLayout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { api, errorMessage } from "@/lib/api";

export const Route = createFileRoute("/forgot-password")({
  head: () => ({
    meta: [
      { title: "Forgot password – ReBuild" },
      { name: "description", content: "Reset your ReBuild account password." },
      { property: "og:title", content: "Forgot password – ReBuild" },
      { property: "og:description", content: "Request a password reset link." },
    ],
  }),
  component: Page,
});

function Page() {
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [busy, setBusy] = useState(false);
  return (
    <AuthLayout title="Forgot password" subtitle="We'll email you a reset link.">
      {sent ? (
        <p className="rounded-lg bg-leaf-soft p-4 text-sm">If an account exists for {email}, a reset link is on its way.</p>
      ) : (
        <form
          className="space-y-4"
          onSubmit={async (e) => {
            e.preventDefault();
            setBusy(true);
            try {
              await api.post("/auth/forgot-password", { email });
              setSent(true);
            } catch (err) {
              toast.error(errorMessage(err));
            } finally {
              setBusy(false);
            }
          }}
        >
          <div>
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
          </div>
          <Button type="submit" className="w-full" disabled={busy}>Send reset link</Button>
        </form>
      )}
      <Link to="/login" className="mt-6 block text-center text-sm text-secondary">Back to sign in</Link>
    </AuthLayout>
  );
}
