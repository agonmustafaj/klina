export default function AboutPage() {
  return (
    <div className="mx-auto max-w-3xl px-6 py-8">
      <h1 className="font-display text-2xl font-semibold text-white">About CityOS</h1>
      <div className="mt-4 space-y-4 text-sm leading-relaxed text-slate-300">
        <p>
          CityOS is a digital twin of the{" "}
          <strong className="text-white">Municipality of Klina</strong> (Klinë),
          Kosovo. Scope is the full municipal territory — approximately 308.8 km²
          and ~54 settlements — with the official admin boundary as source of truth.
        </p>
        <p>
          Geographic features are acquired from OpenStreetMap via Geofabrik and
          clipped to the verified boundary. The platform never fabricates
          buildings, roads, statistics, or 3D city models.
        </p>
        <p>
          Stack: Next.js App Router, MapLibre (2D), CesiumJS (3D when coverage
          exists), FastAPI, PostGIS, Docker Compose.
        </p>
        <p className="text-slate-500">
          Map data © OpenStreetMap contributors. Geofabrik extracts used under
          OSM license terms.
        </p>
      </div>
    </div>
  );
}
