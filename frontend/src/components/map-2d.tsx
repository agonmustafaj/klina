"use client";

import { useEffect, useRef } from "react";
import * as maplibregl from "maplibre-gl";
import type { GeoJSONSource, Map } from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import { getApiBase } from "@/lib/api";

/** Approximate Klina municipality center — map only; features come from API. */
const KLINA_CENTER: [number, number] = [20.62, 42.62];
const KLINA_ZOOM = 10.5;

// Next.js / Turbopack often breaks the bundled MapLibre worker URL.
// Prefer the copy under /public; fall back to CDN if missing.
if (typeof window !== "undefined") {
  maplibregl.setWorkerUrl("/maplibre-gl-worker.mjs");
}

type Props = {
  activeLayers: string[];
};

export function Map2D({ activeLayers }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<Map | null>(null);

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: {
        version: 8,
        sources: {
          basemap: {
            type: "raster",
            // Carto dark tiles (OSM data) — official tile.openstreetmap.org often
            // blocks/refuses browser app traffic and causes empty Explore maps.
            tiles: [
              "https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
              "https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
              "https://c.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
            ],
            tileSize: 256,
            attribution: "© OpenStreetMap contributors © CARTO",
          },
        },
        layers: [
          {
            id: "basemap",
            type: "raster",
            source: "basemap",
          },
        ],
      },
      center: KLINA_CENTER,
      zoom: KLINA_ZOOM,
    });

    map.addControl(new maplibregl.NavigationControl({ visualizePitch: true }), "top-right");
    mapRef.current = map;

    map.on("load", async () => {
      const base = getApiBase();

      const addGeo = async (
        key: string,
        path: string,
        layer: maplibregl.AddLayerObject,
        outline?: maplibregl.AddLayerObject,
      ) => {
        try {
          const res = await fetch(`${base}${path}`);
          const data = (await res.json()) as GeoJSON.FeatureCollection;
          map.addSource(key, { type: "geojson", data });
          map.addLayer(layer);
          if (outline && data.features?.length) {
            map.addLayer(outline);
          }
        } catch {
          // Keep basemap; empty/missing layers stay off without fabricated data
        }
      };

      await addGeo(
        "boundary",
        "/api/v1/geo/boundary",
        {
          id: "boundary",
          type: "fill",
          source: "boundary",
          paint: {
            "fill-color": "#2dd4bf",
            "fill-opacity": 0.12,
            "fill-outline-color": "#5eead4",
          },
          layout: { visibility: "visible" },
        },
        {
          id: "boundary-outline",
          type: "line",
          source: "boundary",
          paint: {
            "line-color": "#5eead4",
            "line-width": 2,
          },
        },
      );

      await addGeo("roads", "/api/v1/geo/roads?limit=5000", {
        id: "roads",
        type: "line",
        source: "roads",
        paint: {
          "line-color": "#94a3b8",
          "line-width": 1.4,
        },
        layout: { visibility: "visible" },
      });

      await addGeo("buildings", "/api/v1/geo/buildings?limit=5000", {
        id: "buildings",
        type: "fill",
        source: "buildings",
        paint: {
          "fill-color": "#f59e0b",
          "fill-opacity": 0.55,
          "fill-outline-color": "#fbbf24",
        },
        layout: { visibility: "visible" },
      });

      await addGeo("settlements", "/api/v1/geo/settlements?limit=500", {
        id: "settlements",
        type: "circle",
        source: "settlements",
        paint: {
          "circle-radius": 5,
          "circle-color": "#38bdf8",
          "circle-stroke-width": 1,
          "circle-stroke-color": "#0f172a",
        },
        layout: { visibility: "visible" },
      });
    });

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !map.isStyleLoaded()) return;
    for (const key of ["boundary", "boundary-outline", "roads", "buildings", "settlements"]) {
      if (!map.getLayer(key)) continue;
      const baseKey = key === "boundary-outline" ? "boundary" : key;
      const on = activeLayers.includes(baseKey);
      map.setLayoutProperty(key, "visibility", on ? "visible" : "none");
    }
  }, [activeLayers]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;
    const base = getApiBase();
    const refresh = async (key: string, path: string) => {
      if (!map.getSource(key)) return;
      try {
        const res = await fetch(`${base}${path}`);
        const data = await res.json();
        (map.getSource(key) as GeoJSONSource).setData(data);
      } catch {
        /* keep previous / empty */
      }
    };
    if (activeLayers.includes("boundary")) refresh("boundary", "/api/v1/geo/boundary");
    if (activeLayers.includes("roads")) refresh("roads", "/api/v1/geo/roads?limit=5000");
    if (activeLayers.includes("buildings")) refresh("buildings", "/api/v1/geo/buildings?limit=5000");
    if (activeLayers.includes("settlements"))
      refresh("settlements", "/api/v1/geo/settlements?limit=500");
  }, [activeLayers]);

  return <div ref={containerRef} className="h-full w-full" />;
}
