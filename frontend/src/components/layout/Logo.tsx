import { Link } from "@tanstack/react-router";
import { Recycle } from "lucide-react";

export function Logo({ inverted = false }: { inverted?: boolean }) {
  return (
    <Link to="/" className="flex items-center gap-2">
      <span className="grid size-8 place-items-center rounded-lg bg-leaf text-primary">
        <Recycle className="size-4.5" strokeWidth={2.5} />
      </span>
      <span className={`font-display text-lg font-bold ${inverted ? "text-primary-foreground" : "text-primary"}`}>
        Re<span className="text-leaf">Build</span>
      </span>
    </Link>
  );
}
