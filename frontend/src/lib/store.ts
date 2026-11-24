import { create } from "zustand";

export type MapMode = "2d" | "3d";

type UiState = {
  mapMode: MapMode;
  activeLayers: string[];
  sidebarCollapsed: boolean;
  setMapMode: (mode: MapMode) => void;
  toggleLayer: (layer: string) => void;
  setSidebarCollapsed: (v: boolean) => void;
};

export const useUiStore = create<UiState>((set, get) => ({
  mapMode: "2d",
  activeLayers: ["boundary", "roads", "settlements"],
  sidebarCollapsed: false,
  setMapMode: (mapMode) => set({ mapMode }),
  toggleLayer: (layer) => {
    const current = get().activeLayers;
    set({
      activeLayers: current.includes(layer)
        ? current.filter((l) => l !== layer)
        : [...current, layer],
    });
  },
  setSidebarCollapsed: (sidebarCollapsed) => set({ sidebarCollapsed }),
}));
