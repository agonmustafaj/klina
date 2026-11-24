"use client";

import dynamic from "next/dynamic";
import { useUiStore } from "@/lib/store";
import { cn } from "@/lib/utils";

const Map2D = dynamic(() => import("@/components/map-2d").then((m) => m.Map2D), {
  ssr: false,
  loading: () => <div className="flex h-full items-center justify-center text-slate-400">Loading map…</div>,
});

const Map3D = dynamic(() => import("@/components/map-3d").then((m) => m.Map3D), {
  ssr: false,
  loading: () => <div className="flex h-full items-center justify-center text-slate-400">Loading 3D…</div>,
});

const LAYER_TOGGLES = [
  { id: "boundary", label: "Boundary" },
  { id: "roads", label: "Roads" },
  { id: "buildings", label: "Buildings" },
  { id: "settlements", label: "Settlements" },
];

export default function ExplorePage() {
  const { mapMode, setMapMode, activeLayers, toggleLayer } = useUiStore();

  return (
    <div className="relative h-full w-full">
      {/* Map owns the viewport */}
      <div className="absolute inset-0">
        {mapMode === "2d" ? <Map2D activeLayers={activeLayers} /> : <Map3D />}
      </div>

      <div className="pointer-events-none absolute inset-x-0 top-0 z-10 flex items-start justify-between p-3">
        <div className="pointer-events-auto rounded-md border border-white/10 bg-panel/90 px-3 py-2 backdrop-blur">
          <p className="text-[10px] uppercase tracking-[0.18em] text-slate-500">Explore</p>
          <p className="font-display text-sm text-white">Klina Municipality</p>
        </div>

        <div className="pointer-events-auto flex gap-1 rounded-md border border-white/10 bg-panel/90 p-1 backdrop-blur">
          {(["2d", "3d"] as const).map((mode) => (
            <button
              key={mode}
              type="button"
              onClick={() => setMapMode(mode)}
              className={cn(
                "rounded px-3 py-1.5 text-xs font-medium uppercase tracking-wide transition",
                mapMode === mode
                  ? "bg-teal-500/25 text-teal-200"
                  : "text-slate-400 hover:text-white",
              )}
            >
              {mode}
            </button>
          ))}
        </div>
      </div>

      {mapMode === "2d" && (
        <div className="pointer-events-auto absolute bottom-4 left-3 z-10 w-48 rounded-md border border-white/10 bg-panel/90 p-3 backdrop-blur">
          <p className="mb-2 text-[10px] uppercase tracking-[0.18em] text-slate-500">Layers</p>
          <ul className="space-y-1.5">
            {LAYER_TOGGLES.map((layer) => (
              <li key={layer.id}>
                <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-300">
                  <input
                    type="checkbox"
                    checked={activeLayers.includes(layer.id)}
                    onChange={() => toggleLayer(layer.id)}
                    className="rounded border-white/20 bg-ink text-teal-500 focus:ring-teal-500/40"
                  />
                  {layer.label}
                </label>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
