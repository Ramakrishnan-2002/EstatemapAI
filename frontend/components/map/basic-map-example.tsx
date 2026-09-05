"use client";

import React from "react";
import { Map, MapControls } from "@/components/ui/map";

/**
 * Basic MapLibre/mapcn working example with explicit container dimensions
 * and default tiled basemap.
 */
export function BasicMapExample() {
  return (
    <div className="h-[400px] w-full overflow-hidden rounded-lg border border-border">
      <Map center={[77.5946, 12.9716]} zoom={12}>
        <MapControls
          position="top-right"
          showZoom={true}
          showCompass={true}
          showLocate={true}
          showFullscreen={false}
        />
      </Map>
    </div>
  );
}
