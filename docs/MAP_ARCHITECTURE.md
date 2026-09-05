# EstateMap AI — Map Architecture & Mapcn Integration

## 1. Mapcn Integration Overview
EstateMap AI uses **[mapcn](https://www.mapcn.dev/)** as the official React map component library.
Under the hood, mapcn wraps **MapLibre GL** for fast, WebGL/WebGPU-accelerated vector tile rendering.

### Architecture Stack:
```
FastAPI PostGIS Endpoint (e.g. /api/v1/properties)
         │ (GeoJSON FeatureCollection or Property entities)
         ▼
Next.js Client State / TanStack Query
         │ (Normalized [longitude, latitude] coordinates)
         ▼
EstateMap Composition Layer (<MapContainer>, <EstateMap>, <PropertyMarker>, <PropertyPopup>)
         │
         ▼
Official mapcn Registry Component (@/components/ui/map: <Map>, <MapControls>, <MapMarker>, <MarkerContent>, <MarkerPopup>)
         │
         ▼
MapLibre GL Core Engine (OpenStreetMap/Carto Positron vector tiles)
```

---

## 2. Official mapcn Registry Installation
- **Location**: `frontend/components/ui/map.tsx`
- **Installation Standard**: Extracted cleanly from official registry definition (`https://mapcn.dev/r/map.json`) with zero invented or custom fake abstractions.
- **Exports**: `Map`, `MapControls`, `MapMarker`, `MarkerContent`, `MarkerPopup`, `MarkerTooltip`, `MarkerLabel`, `MapPopup`, `MapRoute`, `MapArc`, `MapGeoJSON`, `MapClusterLayer`, `useMap`.
- **CSS Integration**: `@import "maplibre-gl/dist/maplibre-gl.css";` and mapcn theme styling embedded in `frontend/app/globals.css`.
- **Basemap Style**: Default tiled style providing street, locality, and landmark context (NOT blank canvas).

---

## 3. Coordinate Conventions & GeoJSON Transformation
- **Rule**: GeoJSON standard specifies **`[longitude, latitude]`** order (`coordinates[0]` = lng, `coordinates[1]` = lat).
- **Utility**: `frontend/lib/geojson.ts`
  - `propertyToFeature(property: Property): GeoJSON.Feature<GeoJSON.Point, PropertyFeatureProperties>`
  - `propertiesToFeatureCollection(properties: Property[]): GeoJSON.FeatureCollection<GeoJSON.Point, PropertyFeatureProperties>`

---

## 4. Custom Real-Estate UI Elements
1. **PropertyMarker (`frontend/components/map/property-marker.tsx`)**:
   - Compact real-estate price pill (e.g. `₹1.85 Cr` / `₹85 L`).
   - Visual states: Normal, Hovered, and Selected (emerald ring, elevation shadow, scaled up).
2. **PropertyPopup (`frontend/components/map/property-popup.tsx`)**:
   - Rich real-estate summary card with property thumbnail, formatted price, BHK/baths, square footage, locality, and direct link to property details `/properties/[id]`.
4. **POIMarker & POIPopup (`frontend/components/map/poi-marker.tsx`, `poi-popup.tsx`)**:
   - Compact, category-color-coded dot markers representing urban amenities (hospitals, schools, transit, supermarkets, parks, pharmacies, banks).
   - Rendered underneath property markers so property price badges retain visual primacy.
   - Non-intrusive popup showing category badge, name, locality, and geodesic distance without fabricated ratings or hours.
5. **POIFilter Widget (`frontend/components/map/poi-filter.tsx`)**:
   - Floating, collapsible category toggle panel overlaid on the interactive map.
   - Triggers debounced viewport POI requests (`GET /api/v1/maps/pois`) when categories are toggled.

---

## 5. Bidirectional Map ↔ List Synchronization
A single source of truth (`selectedPropertyId` & `hoveredPropertyId`) in `SearchContent` (`frontend/app/search/page.tsx`):
- **Card Click/Select -> Map**: Flies to the property `[lng, lat]` and opens the popup.
- **Marker Click -> List**: Smoothly scrolls the corresponding `PropertyCard` into view (`scrollIntoView({ behavior: 'smooth', block: 'nearest' })`) and highlights it with an active ring.
- **Hover Synchronization**: Hovering a card pulses its marker; hovering a marker emphasizes the card.

---

## 6. Rendering Strategy for Scale
- **Small Datasets (< 100 items)**: Rendered via `<MapMarker>` and `<MarkerPopup>` with price pills and animations.
- **Medium Datasets (100 - 5,000 items)**: Delivered as GeoJSON vector sources with client-side clustering via `<MapClusterLayer>`.
- **Large/Dense Datasets (Phase 6+)**: Viewport-bounded PostGIS querying so only visible features within the map bounding box are loaded.
- **POI Density (Phase 7)**: Bounded by viewport bounding box and category filters (capped at 200–500 features per query) to avoid map canvas lag.

