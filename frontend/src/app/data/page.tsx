"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchCoverage, getApiBase } from "@/lib/api";
import { StatusPill } from "@/components/status-pill";
import { EmptyState } from "@/components/empty-state";

export default function DataPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["coverage"],
    queryFn: fetchCoverage,
  });

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <h1 className="font-display text-2xl font-semibold text-white">Data</h1>
      <p className="mt-2 text-sm text-slate-400">
        Provenance and coverage for every CityOS layer. API base:{" "}
        <code className="font-mono text-teal-300">{getApiBase()}</code>
      </p>

      <div className="mt-6">
        {isLoading && <p className="text-sm text-slate-400">Loading…</p>}
        {isError && (
          <EmptyState title="Data unavailable" detail="Coverage API unreachable." />
        )}
        {data && (
          <ul className="space-y-3">
            {data.items.map((item) => (
              <li
                key={item.layer}
                className="rounded-lg border border-white/10 bg-panel px-4 py-3"
              >
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <p className="font-mono text-sm text-white">{item.layer}</p>
                  <StatusPill status={item.status} />
                </div>
                <p className="mt-2 text-xs text-slate-400">{item.notes ?? "—"}</p>
                {item.source && (
                  <p className="mt-1 text-[11px] text-slate-500">
                    Source: {item.source}
                    {item.source_url ? ` · ${item.source_url}` : ""}
                  </p>
                )}
                {item.layer === "3d_buildings" && (
                  <p className="mt-2 text-xs text-amber-300/90">
                    Cesium UI labels missing 3D coverage until real assets exist.
                  </p>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
