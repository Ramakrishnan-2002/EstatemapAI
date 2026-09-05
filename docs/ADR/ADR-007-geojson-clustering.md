# ADR-007: GeoJSON and Client/Server Clustering for Large Spatial Datasets

## Status
Accepted

## Context
Rendering individual HTML DOM markers for thousands of properties causes browser frame drops and high memory consumption.

## Decision
Geographic endpoints return standard GeoJSON `FeatureCollection` objects. The frontend renders these as vector layers with mapcn/MapLibre clustering enabled for dense areas.

## Consequences
- Smooth 60fps panning and zooming even with thousands of property coordinates.
- Reduced payload sizes and simplified serialization.
