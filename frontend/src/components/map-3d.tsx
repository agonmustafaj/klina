"use client";

import { useQuery } from "@tanstack/react-query";
import { AlertTriangle } from "lucide-react";
import { fetchCoverage } from "@/lib/api";

/**
 * Cesium 3D view.
 * Hard rule: never fake a 3D city. Until real 3D assets exist, this panel
 * explicitly labels missing coverage. CesiumJS will be wired when
 * data_coverage.3d_buildings is present/partial with real assets.
 */
export function Map3D() {
  const { data, isLoading, isError } = useQuery({
    queryKey: ["coverage"],
    queryFn: fetchCoverage,
  });

  const threeD = data?.items.find((i) => i.layer === "3d_buildings");
  const hasReal3d = threeD?.status === "present" || (threeD?.status === "partial" && threeD.has_3d);

  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center bg-[radial-gradient(ellipse_at_center,_#152033_0%,_#0b1220_70%)]">
      <div className="absolute inset-0 opacity-[0.07] [background-image:linear-gradient(#94a3b8_1px,transparent_1px),linear-gradient(90deg,#94a3b8_1px,transparent_1px)] [background-size:48px_48px]" />

      <div className="relative z-10 max-w-lg rounded-lg border border-amber-500/30 bg-panel/90 p-6 shadow-xl backdrop-blur">
        <div className="mb-3 flex items-center gap-2 text-amber-300">
          <AlertTriangle className="h-5 w-5" />
          <h2 className="font-display text-lg">3D coverage unavailable</h2>
        </div>
        {isLoading && <p className="text-sm text-slate-400">Checking coverage…</p>}
        {isError && (
          <p className="text-sm text-slate-400">
            Could not reach the coverage API. Data unavailable.
          </p>
        )}
        {!isLoading && !isError && (
          <>
            <p className="text-sm leading-relaxed text-slate-300">
              CityOS does not fabricate 3D city models. Cesium will render only
              verified 3D assets (e.g. buildings with real height tags or future
              LOD2/photogrammetry).
            </p>
            <dl className="mt-4 grid grid-cols-2 gap-3 text-xs text-slate-400">
              <div>
                <dt className="uppercase tracking-wider text-slate-500">Layer</dt>
                <dd className="mt-0.5 text-slate-200">3d_buildings</dd>
              </div>
              <div>
                <dt className="uppercase tracking-wider text-slate-500">Status</dt>
                <dd className="mt-0.5 text-amber-200">{threeD?.status ?? "missing"}</dd>
              </div>
              <div className="col-span-2">
                <dt className="uppercase tracking-wider text-slate-500">Notes</dt>
                <dd className="mt-0.5 text-slate-300">
                  {threeD?.notes ?? "No real 3D coverage imported."}
                </dd>
              </div>
            </dl>
            {hasReal3d ? (
              <p className="mt-4 text-sm text-teal-300">
                Partial height attributes detected — Cesium extrusion wiring is
                next once footprints are confirmed in Explore 2D.
              </p>
            ) : (
              <p className="mt-4 text-sm text-slate-500">
                Switch to 2D Explore for the live MapLibre basemap and imported
                OSM layers.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
