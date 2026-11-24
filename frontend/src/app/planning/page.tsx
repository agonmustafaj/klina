import { EmptyState } from "@/components/empty-state";

export default function PlanningPage() {
  return (
    <div className="mx-auto max-w-4xl px-6 py-8">
      <h1 className="font-display text-2xl font-semibold text-white">Planning</h1>
      <p className="mt-2 text-sm text-slate-400">
        Zoning and planning overlays require official open sources before display.
      </p>
      <div className="mt-6">
        <EmptyState
          title="Data unavailable"
          detail="No planning / cadastral open layers have been imported."
        />
      </div>
    </div>
  );
}
