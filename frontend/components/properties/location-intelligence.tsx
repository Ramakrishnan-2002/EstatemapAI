"use client";

import React, { useEffect, useState } from "react";
import { Loader2, AlertCircle } from "lucide-react";
import type { LocationIntelligenceResponse, POICategory } from "@/types";
import { POI_CATEGORIES, POI_CATEGORY_LABELS } from "@/types";
import { getPropertyLocationIntelligence } from "@/lib/api/pois";

interface LocationIntelligenceProps {
  propertyId: number;
  radiusKm?: number;
  className?: string;
}

/** Category icon characters — minimal, accessible, no emoji in professional context. */
const CATEGORY_ICONS: Record<POICategory, string> = {
  hospital: "H",
  school: "S",
  transit: "T",
  supermarket: "M",
  park: "P",
  pharmacy: "Rx",
  bank: "B",
};

const CATEGORY_DOT_COLORS: Record<POICategory, string> = {
  hospital: "bg-red-500",
  school: "bg-blue-500",
  transit: "bg-orange-500",
  supermarket: "bg-teal-500",
  park: "bg-emerald-500",
  pharmacy: "bg-purple-500",
  bank: "bg-slate-500",
};

const CATEGORY_BG_COLORS: Record<POICategory, string> = {
  hospital: "bg-red-50 text-red-700 border-red-100",
  school: "bg-blue-50 text-blue-700 border-blue-100",
  transit: "bg-orange-50 text-orange-700 border-orange-100",
  supermarket: "bg-teal-50 text-teal-700 border-teal-100",
  park: "bg-emerald-50 text-emerald-700 border-emerald-100",
  pharmacy: "bg-purple-50 text-purple-700 border-purple-100",
  bank: "bg-slate-50 text-slate-700 border-slate-100",
};

function formatDistance(km: number | null): string {
  if (km === null) return "—";
  if (km < 1) return `${Math.round(km * 1000)} m`;
  return `${km.toFixed(1)} km`;
}

/**
 * Location Intelligence summary card for a property.
 *
 * Displays per-category nearest distance and count within radius.
 * Data is computed deterministically by PostGIS — never AI-generated.
 *
 * States: loading | error | no-data | data
 */
export function LocationIntelligence({
  propertyId,
  radiusKm = 3,
  className = "",
}: LocationIntelligenceProps) {
  const [data, setData] = useState<LocationIntelligenceResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setIsLoading(true);
    setError(null);

    getPropertyLocationIntelligence(propertyId, radiusKm)
      .then((resp) => {
        if (!cancelled) setData(resp);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(
            err instanceof Error ? err.message : "Failed to load location data."
          );
        }
      })
      .finally(() => {
        if (!cancelled) setIsLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [propertyId, radiusKm]);

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-baseline justify-between">
        <h2 className="text-lg font-bold tracking-tight text-foreground">
          Location Intelligence
        </h2>
        <span className="text-[11px] text-muted-foreground">
          Nearest POI · count within {radiusKm} km
        </span>
      </div>

      <div className="rounded-lg border border-border bg-card shadow-sm overflow-hidden">
        {isLoading && (
          <div className="flex items-center justify-center gap-2 py-8 text-sm text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin" />
            <span>Computing spatial proximity…</span>
          </div>
        )}

        {!isLoading && error && (
          <div className="flex items-center gap-2 px-4 py-4 text-sm text-muted-foreground">
            <AlertCircle className="h-4 w-4 text-muted-foreground/70 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {!isLoading && !error && !data && (
          <div className="px-4 py-4 text-sm text-muted-foreground">
            No location data available for this property.
          </div>
        )}

        {!isLoading && !error && data && (
          <div className="divide-y divide-border">
            {/* Header row */}
            <div className="grid grid-cols-[1fr_auto_auto] gap-x-4 px-4 py-2 bg-muted/30">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                Category
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground text-right">
                Nearest
              </span>
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground text-right">
                Within {radiusKm} km
              </span>
            </div>

            {/* Data rows */}
            {POI_CATEGORIES.map((category) => {
              const intel = data.categories[category];
              const hasData = intel !== undefined;
              const distance = hasData ? intel.nearest_distance_km : null;
              const count = hasData ? intel.count_within_radius : 0;
              const isPresent = distance !== null;

              return (
                <div
                  key={category}
                  className="grid grid-cols-[1fr_auto_auto] gap-x-4 items-center px-4 py-2.5 hover:bg-muted/20 transition-colors"
                >
                  {/* Category label */}
                  <div className="flex items-center gap-2 min-w-0">
                    <span
                      className={`
                        flex h-5 w-5 shrink-0 items-center justify-center rounded border
                        text-[9px] font-bold leading-none ${CATEGORY_BG_COLORS[category]}
                      `}
                      aria-hidden="true"
                    >
                      {CATEGORY_ICONS[category]}
                    </span>
                    <span className="text-xs font-medium text-foreground truncate">
                      {POI_CATEGORY_LABELS[category]}
                    </span>
                  </div>

                  {/* Nearest distance */}
                  <div className="text-right">
                    <span
                      className={`text-xs font-semibold ${
                        isPresent ? "text-foreground" : "text-muted-foreground"
                      }`}
                    >
                      {formatDistance(distance)}
                    </span>
                  </div>

                  {/* Count */}
                  <div className="text-right min-w-[2.5rem]">
                    <span
                      className={`
                        inline-flex items-center justify-center rounded px-1.5 py-0.5
                        text-[10px] font-semibold tabular-nums
                        ${count > 0
                          ? `${CATEGORY_BG_COLORS[category]} border`
                          : "text-muted-foreground"
                        }
                      `}
                    >
                      {count}
                    </span>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Footer */}
        {!isLoading && !error && data && (
          <div className="border-t border-border px-4 py-2 bg-muted/20">
            <p className="text-[10px] text-muted-foreground">
              Geographic proximity computed from PostGIS spatial data.
              Distances are approximate (WGS84 geodesic). Demo dataset.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
