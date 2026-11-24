const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export type CoverageItem = {
  layer: string;
  status: "present" | "partial" | "missing" | string;
  feature_count: number | null;
  has_3d: boolean;
  source?: string | null;
  source_url?: string | null;
  notes?: string | null;
};

export type CoverageResponse = {
  municipality: string;
  items: CoverageItem[];
  message?: string | null;
};

export type StatsSummary = {
  status: string;
  message?: string;
  counts?: Record<string, number>;
};

async function getJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      Accept: "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    throw new Error(`API ${path} failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export function getApiBase() {
  return API_URL;
}

export async function fetchCoverage(): Promise<CoverageResponse> {
  return getJson("/api/v1/coverage");
}

export async function fetchStats(): Promise<StatsSummary> {
  return getJson("/api/v1/geo/stats/summary");
}

export async function fetchGeoJson(path: string): Promise<GeoJSON.FeatureCollection> {
  return getJson(path);
}

export async function searchPlaces(q: string) {
  return getJson<{
    query: string;
    results: Array<Record<string, unknown>>;
    message?: string | null;
  }>(`/api/v1/geo/search?q=${encodeURIComponent(q)}`);
}
