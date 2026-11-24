import { cn } from "@/lib/utils";

export function StatusPill({ status }: { status: string }) {
  return (
    <span
      className={cn(
        "inline-flex rounded px-2 py-0.5 text-[11px] font-medium uppercase tracking-wide",
        status === "present" && "bg-teal-500/20 text-teal-300",
        status === "partial" && "bg-amber-500/20 text-amber-300",
        status === "missing" && "bg-slate-500/20 text-slate-400",
        !["present", "partial", "missing"].includes(status) &&
          "bg-slate-500/20 text-slate-400",
      )}
    >
      {status}
    </span>
  );
}
