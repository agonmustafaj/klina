"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Building2,
  Database,
  Globe2,
  Info,
  Layers3,
  Map,
  MapPinned,
  Mountain,
  Trees,
  Users,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Overview", icon: Globe2 },
  { href: "/explore", label: "Explore", icon: Map },
  { href: "/settlements", label: "Settlements", icon: MapPinned },
  { href: "/infrastructure", label: "Infrastructure", icon: Building2 },
  { href: "/environment", label: "Environment", icon: Trees },
  { href: "/demographics", label: "Demographics", icon: Users },
  { href: "/planning", label: "Planning", icon: Layers3 },
  { href: "/data", label: "Data", icon: Database },
  { href: "/about", label: "About", icon: Info },
];

export function Shell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const explore = pathname.startsWith("/explore");

  return (
    <div className="flex h-dvh w-full overflow-hidden bg-ink text-slate-100">
      <aside className="flex w-56 shrink-0 flex-col border-r border-white/10 bg-panel">
        <div className="border-b border-white/10 px-4 py-5">
          <div className="flex items-center gap-2">
            <Mountain className="h-5 w-5 text-teal-400" />
            <div>
              <p className="font-display text-lg leading-none tracking-tight text-white">
                CityOS
              </p>
              <p className="mt-1 text-[11px] uppercase tracking-[0.18em] text-slate-400">
                Klina Municipality
              </p>
            </div>
          </div>
        </div>
        <nav className="flex-1 space-y-0.5 overflow-y-auto p-2">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active = href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm transition",
                  active
                    ? "bg-teal-500/15 text-teal-200"
                    : "text-slate-300 hover:bg-white/5 hover:text-white",
                )}
              >
                <Icon className="h-4 w-4 shrink-0 opacity-80" />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="border-t border-white/10 p-3 text-[11px] leading-relaxed text-slate-500">
          Real OSM / Geofabrik data only. Missing layers show as unavailable —
          never fabricated.
        </div>
      </aside>
      <main className={cn("relative min-w-0 flex-1", explore ? "overflow-hidden" : "overflow-y-auto")}>
        {children}
      </main>
    </div>
  );
}
