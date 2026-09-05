# ADR-003: mapcn as Primary React Map System (MapLibre Engine)

## Status
Accepted

## Context
EstateMap AI needs a modern, composable, and customizable React mapping component library that fits seamlessly into the Tailwind / shadcn design system.

## Decision
Use **mapcn** (official documentation: [https://www.mapcn.dev/](https://www.mapcn.dev/)) with MapLibre GL as the foundational mapping component library.

## Alternatives Considered
- **Leaflet / React-Leaflet**: Mature but raster-biased and slower for dense vector layers or WebGL transitions.
- **Mapbox GL JS**: Proprietary license and token billing constraints.
- **Custom React Mapbox wrapper**: Unnecessary maintenance burden when mapcn offers headless, idiomatic React primitives.

## Consequences
- Clean JSX-based map composition (`<Map>`, `<Marker>`, `<Popup>`, `<Source>`, `<Layer>`).
- Fast WebGL rendering powered by open-source MapLibre.
- Isolated map code cleanly separated from core business UI.
