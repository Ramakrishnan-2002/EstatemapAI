"use client";

import React from "react";
import { MapMarker, MarkerContent, MarkerPopup } from "@/components/ui/map";
import type { POICategory, POIGeoJSONFeature } from "@/types";
import { POIPopup } from "./poi-popup";

interface POIMarkerProps {
  feature: POIGeoJSONFeature;
  isSelected?: boolean;
  onClick?: (feature: POIGeoJSONFeature) => void;
}

/**
 * Small dot icon for each POI category.
 * Deliberately compact — does not compete visually with property price badges.
 */
const CATEGORY_COLORS: Record<POICategory, { bg: string; ring: string; dot: string }> = {
  hospital: {
    bg: "bg-red-50 border-red-200",
    ring: "ring-red-300",
    dot: "bg-red-500",
  },
  school: {
    bg: "bg-blue-50 border-blue-200",
    ring: "ring-blue-300",
    dot: "bg-blue-500",
  },
  transit: {
    bg: "bg-orange-50 border-orange-200",
    ring: "ring-orange-300",
    dot: "bg-orange-500",
  },
  supermarket: {
    bg: "bg-teal-50 border-teal-200",
    ring: "ring-teal-300",
    dot: "bg-teal-500",
  },
  park: {
    bg: "bg-emerald-50 border-emerald-200",
    ring: "ring-emerald-300",
    dot: "bg-emerald-500",
  },
  pharmacy: {
    bg: "bg-purple-50 border-purple-200",
    ring: "ring-purple-300",
    dot: "bg-purple-500",
  },
  bank: {
    bg: "bg-slate-50 border-slate-200",
    ring: "ring-slate-300",
    dot: "bg-slate-500",
  },
};

const CATEGORY_LABELS: Record<POICategory, string> = {
  hospital: "Hospital",
  school: "School",
  transit: "Transit",
  supermarket: "Supermarket",
  park: "Park",
  pharmacy: "Pharmacy",
  bank: "Bank",
};

export function POIMarker({ feature, isSelected = false, onClick }: POIMarkerProps) {
  const { properties, geometry } = feature;
  const [longitude, latitude] = geometry.coordinates;
  const category = properties.category;
  const colors = CATEGORY_COLORS[category] ?? {
    bg: "bg-muted border-border",
    ring: "ring-border",
    dot: "bg-muted-foreground",
  };

  const handleClick = (e: MouseEvent) => {
    e.stopPropagation();
    onClick?.(feature);
  };

  const categoryLabel = CATEGORY_LABELS[category] ?? category;

  return (
    <MapMarker longitude={longitude} latitude={latitude} onClick={handleClick}>
      <MarkerContent>
        <button
          type="button"
          aria-label={`${categoryLabel}: ${properties.name}`}
          title={properties.name}
          className={`
            group flex items-center justify-center rounded-full border transition-all duration-150 cursor-pointer
            ${isSelected
              ? `h-5 w-5 ${colors.bg} ${colors.ring} ring-2 shadow-md scale-125 z-20`
              : `h-4 w-4 ${colors.bg} border shadow-sm hover:scale-110 z-10`
            }
          `}
        >
          <span
            className={`rounded-full transition-all duration-150 ${colors.dot} ${
              isSelected ? "h-2.5 w-2.5" : "h-2 w-2"
            }`}
            aria-hidden="true"
          />
        </button>
      </MarkerContent>

      {isSelected && (
        <MarkerPopup closeButton={false} offset={10} anchor="bottom">
          <POIPopup
            name={properties.name}
            category={properties.category}
            subcategory={properties.subcategory}
            locality={properties.locality}
            city={properties.city}
          />
        </MarkerPopup>
      )}
    </MapMarker>
  );
}
