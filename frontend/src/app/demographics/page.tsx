import { EmptyState } from "@/components/empty-state";

export default function DemographicsPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="font-display text-2xl font-semibold text-white">Demographics</h1>
      <p className="mt-2 text-sm text-slate-400">
        Official open demographic series will appear here when acquired and
        attributed. CityOS does not hardcode population charts.
      </p>
      <div className="mt-6">
        <EmptyState
          title="Data unavailable"
          detail="No verified demographics dataset is linked yet."
        />
      </div>
    </div>
  );
}
