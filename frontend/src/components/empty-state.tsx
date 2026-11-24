import { Inbox } from "lucide-react";

export function EmptyState({
  title = "Data unavailable",
  detail,
}: {
  title?: string;
  detail?: string;
}) {
  return (
    <div className="flex flex-col items-center justify-center rounded-lg border border-dashed border-white/15 bg-white/[0.02] px-6 py-14 text-center">
      <Inbox className="mb-3 h-8 w-8 text-slate-500" />
      <p className="font-display text-base text-slate-200">{title}</p>
      {detail && <p className="mt-2 max-w-md text-sm text-slate-400">{detail}</p>}
    </div>
  );
}
