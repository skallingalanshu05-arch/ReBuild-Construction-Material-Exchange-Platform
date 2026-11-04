import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { AuthLayout, FieldError } from "@/components/layout/AuthLayout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { api, errorMessage } from "@/lib/api";

export const Route = createFileRoute("/register")({
  head: () => ({
    meta: [
      { title: "Register your company – ReBuild" },
      { name: "description", content: "Create a ReBuild account to list and source reusable construction materials." },
      { property: "og:title", content: "Register your company – ReBuild" },
      { property: "og:description", content: "Join the construction material exchange." },
    ],
  }),
  component: Register,
});

const schema = z
  .object({
    full_name: z.string().trim().min(2, "Enter your full name").max(100),
    email: z.string().trim().email("Enter a valid email"),
    mobile: z.string().trim().regex(/^\+?[0-9 ]{8,15}$/, "Enter a valid mobile number"),
    password: z.string().min(8, "At least 8 characters"),
    confirm: z.string(),
    company_name: z.string().trim().min(2, "Enter company name").max(150),
    address: z.string().trim().min(3, "Enter address").max(300),
    city: z.string().trim().min(2, "Required"),
    state: z.string().trim().min(2, "Required"),
    country: z.string().trim().min(2, "Required"),
    registration_number: z.string().trim().max(50).optional(),
    capability: z.enum(["supplier", "buyer", "both"]),
  })
  .refine((v) => v.password === v.confirm, { path: ["confirm"], message: "Passwords don't match" });
type V = z.infer<typeof schema>;

const fields: [keyof V, string, string?][] = [
  ["full_name", "Full name"], ["email", "Email", "email"], ["mobile", "Mobile number", "tel"],
  ["password", "Password", "password"], ["confirm", "Confirm password", "password"],
  ["company_name", "Company name"], ["address", "Company address"], ["city", "City"], ["state", "State"], ["country", "Country"],
  ["registration_number", "Company registration number (optional)"],
];

function Register() {
  const navigate = useNavigate();
  const { register, handleSubmit, formState } = useForm<V>({ resolver: zodResolver(schema), defaultValues: { capability: "both", country: "India" } });
  const onSubmit = handleSubmit(async ({ confirm: _c, ...v }) => {
    try {
      // ASSUMED endpoint: POST /auth/register
      await api.post("/auth/register", v);
      toast.success("Account created — please sign in");
      navigate({ to: "/login" });
    } catch (e) {
      toast.error(errorMessage(e));
    }
  });

  return (
    <AuthLayout title="Register your company" subtitle="List surplus, source materials, or both.">
      <form onSubmit={onSubmit} className="grid gap-4 sm:grid-cols-2">
        {fields.map(([k, label, type]) => (
          <div key={k} className={["address", "registration_number", "email"].includes(k) ? "sm:col-span-2" : ""}>
            <Label htmlFor={k}>{label}</Label>
            <Input id={k} type={type ?? "text"} {...register(k)} />
            <FieldError msg={formState.errors[k]?.message} />
          </div>
        ))}
        <fieldset className="sm:col-span-2">
          <legend className="mb-2 text-sm font-medium">Account capabilities</legend>
          <div className="grid grid-cols-3 gap-2">
            {(["supplier", "buyer", "both"] as const).map((c) => (
              <label key={c} className="flex cursor-pointer items-center justify-center gap-2 rounded-lg border p-3 text-sm capitalize has-[:checked]:border-leaf has-[:checked]:bg-leaf-soft">
                <input type="radio" value={c} className="accent-primary" {...register("capability")} /> {c}
              </label>
            ))}
          </div>
        </fieldset>
        <Button type="submit" className="sm:col-span-2" disabled={formState.isSubmitting}>{formState.isSubmitting ? "Creating account…" : "Create account"}</Button>
        <p className="text-center text-sm text-muted-foreground sm:col-span-2">
          Already registered? <Link to="/login" className="font-semibold text-secondary">Sign in</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
