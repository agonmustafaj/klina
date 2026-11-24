"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchStats } from "@/lib/api";
import { EmptyState } from "@/components/empty-state";

export default function InfrastructurePage() {
  const { data, isLoading } = useQuery({ queryKey: ["stats"], queryFn: fetchStats });

  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="font-display text-2xl font-semibold text-white">Infrastructure</h1>
      <p className="mt-2 text-sm text-slate-400">
        Roads, buildings, and amenities derived from OSM. Counts reflect imported
        features only.
      </p>
      <div className="mt-6">
        {isLoading && <p className="text-sm text-slate-400">Loading…</p>}
        {!isLoading && data?.status !== "ok" && (
          <EmptyState
            title="Data unavailable"
            detail={data?.message ?? "Import OSM layers to populate infrastructure metrics."}
          />
        )}
        {data?.status === "ok" && data.counts && (
          <div className="grid gap-3 sm:grid-cols-2">
            {Object.entries(data.counts).map(([key, value]) => (
              <div key={key} className="rounded-lg border border-white/10 bg-panel p-4">
                <p className="text-[11px] uppercase tracking-wider text-slate-500">{key}</p>
                <p className="mt-2 font-mono text-2xl text-white">{value}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
