import { EmptyState } from "@/components/empty-state";

export default function EnvironmentPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="font-display text-2xl font-semibold text-white">Environment</h1>
      <p className="mt-2 text-sm text-slate-400">
        Landuse, water, and natural features from OSM once imported.
      </p>
      <div className="mt-6">
        <EmptyState
          title="Data unavailable"
          detail="Environmental layers have not been loaded into PostGIS yet. No values are fabricated."
        />
      </div>
    </div>
  );
}
