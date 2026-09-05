"use client";

import React from "react";
import type { POICategory } from "@/types";

interface POIPopupProps {
  name: string;
  category: POICategory;
  subcategory?: string | null;
  locality?: string | null;
  city: string;
  distance_km?: number;
}

/** Human-readable category labels (must stay in sync with types/index.ts). */
const CATEGORY_LABELS: Record<POICategory, string> = {
  hospital: "Hospital",
  school: "School",
  transit: "Transit Stop",
  supermarket: "Supermarket",
  park: "Park",
  pharmacy: "Pharmacy",
  bank: "Bank",
};

/** Category colour accent (subtle, accessible, professional). */
const CATEGORY_COLORS: Record<POICategory, string> = {
  hospital: "text-red-600",
  school: "text-blue-600",
  transit: "text-orange-600",
  supermarket: "text-teal-600",
  park: "text-emerald-600",
  pharmacy: "text-purple-600",
  bank: "text-slate-600",
};

export function POIPopup({ name, category, subcategory, locality, city, distance_km }: POIPopupProps) {
  const label = CATEGORY_LABELS[category] ?? category;
  const accentColor = CATEGORY_COLORS[category] ?? "text-muted-foreground";

  return (
    <div
      className="w-48 overflow-hidden rounded-lg border border-border bg-card shadow-lg"
      role="tooltip"
      aria-label={`${name} — ${label}`}
    >
      <div className="px-3 py-2.5">
        {/* Category badge */}
        <span className={`text-[10px] font-semibold uppercase tracking-widest ${accentColor}`}>
          {label}
          {subcategory && ` · ${subcategory}`}
        </span>

        {/* Name */}
        <p className="mt-0.5 text-xs font-semibold text-foreground leading-tight line-clamp-2">
          {name}
        </p>

        {/* Location */}
        {(locality || city) && (
          <p className="mt-1 text-[11px] text-muted-foreground truncate">
            {locality ? `${locality}, ` : ""}{city}
          </p>
        )}

        {/* Distance — only shown when computed */}
        {distance_km !== undefined && (
          <p className="mt-1.5 text-[11px] font-medium text-foreground">
            <span className="text-muted-foreground">Distance: </span>
            {distance_km < 1
              ? `${Math.round(distance_km * 1000)} m`
              : `${distance_km.toFixed(1)} km`}
          </p>
        )}
      </div>
    </div>
  );
}
