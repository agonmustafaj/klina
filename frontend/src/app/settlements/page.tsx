"use client";

import { useQuery } from "@tanstack/react-query";
import { fetchGeoJson } from "@/lib/api";
import { EmptyState } from "@/components/empty-state";

export default function SettlementsPage() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["settlements"],
    queryFn: () => fetchGeoJson("/api/v1/geo/settlements?limit=500"),
  });

  const features = data?.features ?? [];

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <h1 className="font-display text-2xl font-semibold text-white">Settlements</h1>
      <p className="mt-2 text-sm text-slate-400">
        Place nodes from the OSM clip inside the municipal boundary. Population is
        shown only when present in the source tags.
      </p>

      <div className="mt-6">
        {isLoading && <p className="text-sm text-slate-400">Loading…</p>}
        {(isError || features.length === 0) && !isLoading && (
          <EmptyState
            title="Data unavailable"
            detail="No settlements imported yet. Run the geographic acquisition pipeline, then refresh."
          />
        )}
        {features.length > 0 && (
          <div className="overflow-hidden rounded-lg border border-white/10">
            <table className="w-full text-left text-sm">
              <thead className="bg-panel text-[11px] uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-4 py-2.5">Name</th>
                  <th className="px-4 py-2.5">Type</th>
                  <th className="px-4 py-2.5">Population</th>
                  <th className="px-4 py-2.5">Source</th>
                </tr>
              </thead>
              <tbody>
                {features.map((f, i) => {
                  const p = (f.properties ?? {}) as Record<string, unknown>;
                  return (
                    <tr key={String(p.id ?? i)} className="border-t border-white/5">
                      <td className="px-4 py-2 text-slate-200">{String(p.name ?? "—")}</td>
                      <td className="px-4 py-2 text-slate-400">{String(p.place_type ?? "—")}</td>
                      <td className="px-4 py-2 font-mono text-xs text-slate-400">
                        {p.population != null ? String(p.population) : "Data unavailable"}
                      </td>
                      <td className="px-4 py-2 text-xs text-slate-500">{String(p.source ?? "—")}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
