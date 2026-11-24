"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { ArrowRight } from "lucide-react";
import { fetchCoverage, fetchStats } from "@/lib/api";
import { EmptyState } from "@/components/empty-state";
import { StatusPill } from "@/components/status-pill";

export default function OverviewPage() {
  const coverage = useQuery({ queryKey: ["coverage"], queryFn: fetchCoverage });
  const stats = useQuery({ queryKey: ["stats"], queryFn: fetchStats });

  const present =
    coverage.data?.items.filter((i) => i.status === "present" || i.status === "partial")
      .length ?? 0;
  const total = coverage.data?.items.length ?? 0;

  return (
    <div className="mx-auto max-w-5xl px-6 py-8">
      <header className="mb-8">
        <p className="text-xs uppercase tracking-[0.2em] text-teal-400/80">Digital twin</p>
        <h1 className="mt-2 font-display text-3xl font-semibold tracking-tight text-white">
          Municipality of Klina
        </h1>
        <p className="mt-2 max-w-2xl text-sm leading-relaxed text-slate-400">
          CityOS covers the entire municipal area (~308.8 km², ~54 settlements),
          not the town center alone. Layers come from verified open sources
          (OSM / Geofabrik). Missing data is shown as unavailable — never invented.
        </p>
        <Link
          href="/explore"
          className="mt-5 inline-flex items-center gap-2 rounded-md bg-teal-500/20 px-4 py-2 text-sm text-teal-200 transition hover:bg-teal-500/30"
        >
          Open Explore map <ArrowRight className="h-4 w-4" />
        </Link>
      </header>

      <section className="mb-8 grid gap-4 sm:grid-cols-3">
        <div className="rounded-lg border border-white/10 bg-panel p-4">
          <p className="text-[11px] uppercase tracking-wider text-slate-500">Coverage</p>
          <p className="mt-2 font-mono text-2xl text-white">
            {coverage.isLoading ? "…" : `${present}/${total}`}
          </p>
          <p className="mt-1 text-xs text-slate-400">layers present or partial</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-panel p-4">
          <p className="text-[11px] uppercase tracking-wider text-slate-500">Features</p>
          {stats.data?.status === "ok" && stats.data.counts ? (
            <p className="mt-2 font-mono text-2xl text-white">
              {Object.values(stats.data.counts).reduce((a, b) => a + b, 0)}
            </p>
          ) : (
            <p className="mt-2 text-sm text-slate-400">Data unavailable</p>
          )}
          <p className="mt-1 text-xs text-slate-400">imported geometry count</p>
        </div>
        <div className="rounded-lg border border-white/10 bg-panel p-4">
          <p className="text-[11px] uppercase tracking-wider text-slate-500">3D city</p>
          <p className="mt-2 text-sm text-amber-200">
            {coverage.data?.items.find((i) => i.layer === "3d_buildings")?.status ?? "missing"}
          </p>
          <p className="mt-1 text-xs text-slate-400">Cesium never fakes coverage</p>
        </div>
      </section>

      <section>
        <h2 className="mb-3 font-display text-lg text-white">Layer inventory</h2>
        {coverage.isError && (
          <EmptyState
            title="Data unavailable"
            detail="Could not reach the CityOS API. Start the backend and PostGIS, then refresh."
          />
        )}
        {coverage.data && (
          <div className="overflow-hidden rounded-lg border border-white/10">
            <table className="w-full text-left text-sm">
              <thead className="bg-panel text-[11px] uppercase tracking-wider text-slate-500">
                <tr>
                  <th className="px-4 py-2.5 font-medium">Layer</th>
                  <th className="px-4 py-2.5 font-medium">Status</th>
                  <th className="px-4 py-2.5 font-medium">Count</th>
                  <th className="px-4 py-2.5 font-medium">Notes</th>
                </tr>
              </thead>
              <tbody>
                {coverage.data.items.map((item) => (
                  <tr key={item.layer} className="border-t border-white/5">
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-200">{item.layer}</td>
                    <td className="px-4 py-2.5">
                      <StatusPill status={item.status} />
                    </td>
                    <td className="px-4 py-2.5 font-mono text-xs text-slate-400">
                      {item.feature_count ?? "—"}
                    </td>
                    <td className="px-4 py-2.5 text-xs text-slate-400">
                      {item.notes ?? "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {coverage.data.message && (
              <p className="border-t border-white/5 bg-panel px-4 py-3 text-xs text-slate-400">
                {coverage.data.message}
              </p>
            )}
          </div>
        )}
      </section>
    </div>
  );
}
