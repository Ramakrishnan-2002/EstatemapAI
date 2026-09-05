"use client";

import React, { useEffect, useMemo, useRef, useState } from "react";
import type { MapRef, MapViewport } from "@/components/ui/map";
import { Map, MapControls, MapRoute } from "@/components/ui/map";
import { MapBounds, MapViewportState, POIGeoJSONFeature, Property } from "@/types";
import { PropertyMarker } from "./property-marker";
import { POIMarker } from "./poi-marker";
import { Loader2, MapPin, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EstateMapProps {
  properties: Property[];
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
  initialCenter?: [number, number]; // [longitude, latitude]
  initialZoom?: number;
  className?: string;
  interactive?: boolean;
}

// Default center: Bengaluru City Coordinates [longitude, latitude]
const DEFAULT_CENTER: [number, number] = [77.5946, 12.9716];
const DEFAULT_ZOOM = 12;

export function EstateMap({
  properties,
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
  initialCenter = DEFAULT_CENTER,
  initialZoom = DEFAULT_ZOOM,
  className = "h-full w-full",
  interactive = true,
}: EstateMapProps) {
  const mapRef = useRef<MapRef | null>(null);
  const debounceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const [internalSelectedPOIId, setInternalSelectedPOIId] = useState<number | string | null>(null);
  const activePOIId = selectedPOIId !== undefined ? selectedPOIId : internalSelectedPOIId;

  const [currentCoords, setCurrentCoords] = useState<{ lng: number; lat: number; zoom: number }>({
    lng: initialCenter[0],
    lat: initialCenter[1],
    zoom: initialZoom,
  });
  const [currentBounds, setCurrentBounds] = useState<MapBounds | null>(null);

  // Center calculation from properties or initialCenter
  const center = useMemo<[number, number]>(() => {
    if (properties.length > 0) {
      return [properties[0].longitude, properties[0].latitude];
    }
    return initialCenter;
  }, [properties, initialCenter]);

  // When selectedPropertyId changes, ease or fly map to its coordinates
  useEffect(() => {
    if (!selectedPropertyId || !mapRef.current) return;
    const selected = properties.find((p) => String(p.id) === String(selectedPropertyId));
    if (selected) {
      try {
        mapRef.current.easeTo({
          center: [selected.longitude, selected.latitude],
          zoom: Math.max(mapRef.current.getZoom(), 13),
          duration: 600,
        });
      } catch {
        // Safe fallback if map is transitioning
      }
    }
  }, [selectedPropertyId, properties]);

  // When route coordinates change, fit the map view to contain the entire route
  useEffect(() => {
    if (!route || !route.coordinates || route.coordinates.length < 2 || !mapRef.current) return;

    try {
      let minLng = Infinity;
      let minLat = Infinity;
      let maxLng = -Infinity;
      let maxLat = -Infinity;

      for (const [lng, lat] of route.coordinates) {
        if (lng < minLng) minLng = lng;
        if (lng > maxLng) maxLng = lng;
        if (lat < minLat) minLat = lat;
        if (lat > maxLat) maxLat = lat;
      }

      mapRef.current.fitBounds(
        [
          [minLng, minLat],
          [maxLng, maxLat],
        ],
        {
          padding: { top: 60, bottom: 60, left: 60, right: 60 },
          duration: 800,
          maxZoom: 15,
        }
      );
    } catch {
      // Safe fallback if map is not ready
    }
  }, [route]);


  const handleViewportChange = (vp: MapViewport) => {
    const [lng, lat] = vp.center;
    setCurrentCoords({ lng, lat, zoom: vp.zoom });

    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    debounceTimerRef.current = setTimeout(() => {
      if (mapRef.current) {
        const bounds = mapRef.current.getBounds();
        if (bounds) {
          const mapBounds: MapBounds = {
            north: bounds.getNorth(),
            south: bounds.getSouth(),
            east: bounds.getEast(),
            west: bounds.getWest(),
          };
          setCurrentBounds(mapBounds);

          onViewportChange?.({
            longitude: lng,
            latitude: lat,
            zoom: vp.zoom,
            pitch: vp.pitch,
            bearing: vp.bearing,
            bounds: mapBounds,
          });
        }
      }
    }, 250);
  };

  const handleSearchThisAreaClick = () => {
    if (currentBounds && onSearchThisArea) {
      onSearchThisArea(currentBounds);
    }
  };

  return (
    <div
      className={`relative h-full w-full overflow-hidden rounded-lg border border-border bg-card shadow-xs ${className}`}
      data-testid="estatemap-interactive-map"
      aria-label="Interactive real estate discovery map"
    >
      <Map
        ref={mapRef}
        center={center}
        zoom={initialZoom}
        interactive={interactive}
        onViewportChange={handleViewportChange}
      >
        <MapControls
          position="top-right"
          showZoom={true}
          showCompass={true}
          showLocate={true}
          showFullscreen={false}
        />

        {/* Active Commute Route Layer */}
        {route && route.coordinates && route.coordinates.length >= 2 && (
          <MapRoute
            id="commute-route"
            coordinates={route.coordinates}
            color={route.color || "#3b82f6"}
            width={4}
            opacity={0.85}
          />
        )}

        {/* Points of Interest (POI) Layer */}
        {pois.map((poi) => {
          const isSelected = String(poi.id) === String(activePOIId);
          return (
            <POIMarker
              key={`poi-${poi.id}`}
              feature={poi}
              isSelected={isSelected}
              onClick={(feat) => {
                setInternalSelectedPOIId(feat.id);
                onSelectPOI?.(feat);
              }}
            />
          );
        })}

        {/* Property Markers */}
        {properties.map((property) => {
          const isSelected = String(property.id) === String(selectedPropertyId);
          const isHovered = String(property.id) === String(hoveredPropertyId);

          return (
            <PropertyMarker
              key={property.id}
              property={property}
              isSelected={isSelected}
              isHovered={isHovered}
              onClick={(p) => {
                setInternalSelectedPOIId(null);
                onSelectProperty?.(p);
              }}
              onMouseEnter={(p) => onHoverProperty?.(p)}
              onMouseLeave={() => onHoverProperty?.(null)}
            />
          );
        })}
      </Map>

      {/* "Search this area" Floating Button */}
      {showSearchThisArea && (
        <div className="absolute top-4 left-1/2 -translate-x-1/2 z-20 transition-all duration-200 ease-out animate-in fade-in slide-in-from-top-2">
          <Button
            size="sm"
            onClick={handleSearchThisAreaClick}
            disabled={isSearchingArea}
            className="rounded-full bg-background/95 hover:bg-background text-foreground border border-border/80 shadow-md backdrop-blur-md px-4 py-1.5 text-xs font-semibold flex items-center gap-1.5 transition-transform active:scale-95 cursor-pointer"
          >
            {isSearchingArea ? (
              <>
                <Loader2 className="h-3.5 w-3.5 animate-spin text-emerald-600" />
                <span>Searching area...</span>
              </>
            ) : (
              <>
                <RefreshCw className="h-3.5 w-3.5 text-emerald-600" />
                <span>Search this area</span>
              </>
            )}
          </Button>
        </div>
      )}

      {/* Floating Status & Coordinate Badge */}
      <div className="absolute bottom-3 left-3 z-10 flex items-center gap-2 pointer-events-none">
        <div className="flex items-center gap-1.5 rounded-md border border-border/80 bg-background/90 px-2.5 py-1 text-[11px] font-medium text-foreground backdrop-blur-xs shadow-xs">
          <MapPin className="h-3 w-3 text-emerald-600" />
          <span>
            {currentCoords.lat.toFixed(4)}° N, {currentCoords.lng.toFixed(4)}° E
          </span>
          <span className="text-muted-foreground ml-1">· Zoom {currentCoords.zoom.toFixed(1)}</span>
        </div>
        <div className="hidden sm:flex items-center rounded-md border border-border/80 bg-background/90 px-2 py-1 text-[11px] font-medium text-muted-foreground backdrop-blur-xs shadow-xs">
          <span>{properties.length} active listings</span>
        </div>
      </div>

      {/* Empty State Overlay */}
      {properties.length === 0 && !isSearchingArea && (
        <div className="absolute inset-0 z-20 flex items-center justify-center bg-background/40 backdrop-blur-xs pointer-events-none">
          <div className="rounded-lg border border-border bg-card/95 p-4 text-center shadow-lg pointer-events-auto">
            <p className="text-xs font-semibold text-foreground">No properties in this viewport</p>
            <p className="mt-1 text-[11px] text-muted-foreground">
              Try adjusting your filters or panning to another locality.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
