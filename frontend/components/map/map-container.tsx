"use client";

import React from "react";
import { MapBounds, MapViewportState, POIGeoJSONFeature, Property } from "@/types";
import { EstateMap } from "./estate-map";

interface MapContainerProps {
  className?: string;
  properties?: Property[];
  pois?: POIGeoJSONFeature[];
  route?: { coordinates: [number, number][]; color?: string; name?: string } | null;
  selectedPropertyId?: number | string | null;
  hoveredPropertyId?: number | string | null;
  selectedPOIId?: number | string | null;
  onSelectProperty?: (property: Property | null) => void;
  onHoverProperty?: (property: Property | null) => void;
  onSelectPOI?: (poi: POIGeoJSONFeature | null) => void;
  onViewportChange?: (viewport: MapViewportState) => void;
  onSearchThisArea?: (bounds: MapBounds) => void;
  showSearchThisArea?: boolean;
  isSearchingArea?: boolean;
  latitude?: number;
  longitude?: number;
  zoom?: number;
  interactive?: boolean;
}

export function MapContainer({
  className,
  properties = [],
  pois = [],
  route = null,
  selectedPropertyId,
  hoveredPropertyId,
  selectedPOIId,
  onSelectProperty,
  onHoverProperty,
  onSelectPOI,
  onViewportChange,
  onSearchThisArea,
  showSearchThisArea = false,
  isSearchingArea = false,
  latitude = 12.9716,
  longitude = 77.5946,
  zoom = 12,
  interactive = true,
}: MapContainerProps) {
  return (
    <div className={`h-full w-full ${className || ""}`} data-testid="mapcn-container-boundary">
      <EstateMap
        properties={properties}
        pois={pois}
        route={route}
        selectedPropertyId={selectedPropertyId}
        hoveredPropertyId={hoveredPropertyId}
        selectedPOIId={selectedPOIId}
        onSelectProperty={onSelectProperty}
        onHoverProperty={onHoverProperty}
        onSelectPOI={onSelectPOI}
        onViewportChange={onViewportChange}
        onSearchThisArea={onSearchThisArea}
        showSearchThisArea={showSearchThisArea}
        isSearchingArea={isSearchingArea}
        initialCenter={[longitude, latitude]}
        initialZoom={zoom}
        interactive={interactive}
      />
    </div>
  );
}

