"use client";

import React from "react";
import { MapMarker, MarkerContent, MarkerPopup } from "@/components/ui/map";
import { Property } from "@/types";
import { formatPrice } from "@/lib/formatters/currency";
import { PropertyPopup } from "./property-popup";

interface PropertyMarkerProps {
  property: Property;
  isSelected?: boolean;
  isHovered?: boolean;
  onClick?: (property: Property) => void;
  onMouseEnter?: (property: Property) => void;
  onMouseLeave?: (property: Property) => void;
}

export function PropertyMarker({
  property,
  isSelected = false,
  isHovered = false,
  onClick,
  onMouseEnter,
  onMouseLeave,
}: PropertyMarkerProps) {
  const priceDisplay = formatPrice(property.price);

  const handleClick = (e: MouseEvent) => {
    e.stopPropagation();
    onClick?.(property);
  };

  const handleMouseEnter = () => {
    onMouseEnter?.(property);
  };

  const handleMouseLeave = () => {
    onMouseLeave?.(property);
  };

  return (
    <MapMarker
      longitude={property.longitude}
      latitude={property.latitude}
      onClick={handleClick}
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
    >
      <MarkerContent>
        <button
          type="button"
          aria-label={`Property at ${property.locality}, ${priceDisplay}`}
          className={`group flex items-center justify-center rounded-full px-2.5 py-1 text-xs font-bold tracking-tight shadow-md transition-all duration-200 cursor-pointer select-none ${
            isSelected
              ? "bg-emerald-600 text-white ring-2 ring-emerald-400 scale-110 z-30 shadow-lg"
              : isHovered
              ? "bg-foreground text-background scale-105 z-20"
              : "bg-card text-foreground border border-border/80 hover:bg-foreground hover:text-background hover:scale-105 z-10"
          }`}
        >
          <span>{priceDisplay}</span>
        </button>
      </MarkerContent>

      {/* Render Popup when marker is selected */}
      {isSelected && (
        <MarkerPopup closeButton={false} offset={12} anchor="bottom">
          <PropertyPopup property={property} />
        </MarkerPopup>
      )}
    </MapMarker>
  );
}
