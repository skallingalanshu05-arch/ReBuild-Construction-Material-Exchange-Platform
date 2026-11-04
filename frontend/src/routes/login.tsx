import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { toast } from "sonner";
import { AuthLayout, FieldError } from "@/components/layout/AuthLayout";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useAuth } from "@/lib/auth";
import { errorMessage } from "@/lib/api";

export const Route = createFileRoute("/login")({
  head: () => ({
    meta: [
      { title: "Sign in – ReBuild" },
      { name: "description", content: "Sign in to your ReBuild company account." },
      { property: "og:title", content: "Sign in – ReBuild" },
      { property: "og:description", content: "Access your ReBuild dashboard." },
    ],
  }),
  component: Login,
});

const schema = z.object({ email: z.string().trim().email("Enter a valid email"), password: z.string().min(1, "Enter your password"), remember: z.boolean() });

function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const { register, handleSubmit, formState } = useForm<z.infer<typeof schema>>({ resolver: zodResolver(schema), defaultValues: { remember: true } });

  const onSubmit = handleSubmit(async (v) => {
    try {
      await login(v.email, v.password, v.remember);
      toast.success("Welcome back");
      navigate({ to: "/app" });
    } catch (e) {
      toast.error(errorMessage(e));
    }
  });

  return (
    <AuthLayout title="Sign in" subtitle="Welcome back to ReBuild.">
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <Label htmlFor="email">Email</Label>
          <Input id="email" type="email" autoComplete="email" {...register("email")} />
          <FieldError msg={formState.errors.email?.message} />
        </div>
        <div>
          <div className="flex justify-between">
            <Label htmlFor="password">Password</Label>
            <Link to="/forgot-password" className="text-xs text-secondary hover:underline">Forgot password?</Link>
          </div>
          <Input id="password" type="password" autoComplete="current-password" {...register("password")} />
          <FieldError msg={formState.errors.password?.message} />
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input type="checkbox" className="accent-primary" {...register("remember")} /> Remember me
        </label>
        <Button type="submit" className="w-full" disabled={formState.isSubmitting}>{formState.isSubmitting ? "Signing in…" : "Sign in"}</Button>
        <p className="text-center text-sm text-muted-foreground">
          New to ReBuild? <Link to="/register" className="font-semibold text-secondary">Register your company</Link>
        </p>
      </form>
    </AuthLayout>
  );
}
