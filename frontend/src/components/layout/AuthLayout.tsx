import type { ReactNode } from "react";
import { Logo } from "./Logo";
import hero from "@/assets/hero-materials.jpg";
import { isApiConfigured } from "@/lib/api";

export function AuthLayout({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      <div className="flex flex-col px-6 py-8 sm:px-12">
        <Logo />
        <div className="mx-auto flex w-full max-w-md flex-1 flex-col justify-center py-10">
          <h1 className="text-3xl font-bold text-primary">{title}</h1>
          {subtitle && <p className="mt-2 text-muted-foreground">{subtitle}</p>}
          {!isApiConfigured && (
            <p className="mt-4 rounded-lg border border-warning/50 bg-warning/10 p-3 text-sm">
              The backend isn't connected yet, so this form can't submit.
            </p>
          )}
          <div className="mt-8">{children}</div>
        </div>
      </div>
      <div className="relative hidden lg:block">
        <img src={hero} alt="" className="absolute inset-0 size-full object-cover" />
        <div className="absolute inset-0 bg-hero" />
        <p className="absolute bottom-12 left-12 max-w-sm font-display text-3xl font-bold text-primary-foreground">
          Give construction materials a second life.
        </p>
      </div>
    </div>
  );
}

export function FieldError({ msg }: { msg?: string }) {
  return msg ? <p className="mt-1 text-xs text-destructive">{msg}</p> : null;
}
