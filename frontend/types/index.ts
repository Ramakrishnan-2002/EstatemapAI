// ==========================================
// User & Authentication Types
// ==========================================

export interface User {
  id: number;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at?: string | null;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
}

// ==========================================
// Property Domain Types
// ==========================================

export interface Amenity {
  id: number;
  name: string;
  category: string;
  icon?: string | null;
}

export interface PropertyImage {
  id: number;
  image_url: string;
  display_order: number;
}

export interface Property {
  id: number;
  owner_id: number;
  title: string;
  description?: string | null;
  price: number;
  property_type: string;
  bedrooms?: number | null;
  bathrooms?: number | null;
  area_sqft: number;
  address: string;
  city: string;
  locality: string;
  latitude: number;
  longitude: number;
  status: string;
  images: PropertyImage[];
  amenities: Amenity[];
  created_at: string;
  updated_at?: string | null;
}

export interface PropertyCreate {
  title: string;
  description?: string | null;
  price: number;
  property_type: string;
  bedrooms?: number | null;
  bathrooms?: number | null;
  area_sqft: number;
  address: string;
  city: string;
  locality: string;
  latitude: number;
  longitude: number;
  status?: string;
  image_urls?: string[];
  amenity_ids?: number[];
}

export interface PropertyUpdate {
  title?: string;
  description?: string | null;
  price?: number;
  property_type?: string;
  bedrooms?: number | null;
  bathrooms?: number | null;
  area_sqft?: number;
  address?: string;
  city?: string;
  locality?: string;
  latitude?: number;
  longitude?: number;
  status?: string;
  image_urls?: string[];
  amenity_ids?: number[];
}

export interface PropertyFilterParams {
  city?: string;
  locality?: string;
  property_type?: string;
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
  bathrooms?: number;
  status?: string;
  sort_by?: "newest" | "oldest" | "price_asc" | "price_desc" | "area_asc" | "area_desc" | "ranked";
  page?: number;
  page_size?: number;
}


export interface PaginatedPropertyResponse {
  items: Property[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ==========================================
// Geo & Map Types (For mapcn / MapLibre)
// ==========================================

export interface SpatialFilterParams {
  min_price?: number;
  max_price?: number;
  property_type?: string;
  bedrooms?: number;
  bathrooms?: number;
  status?: string;
  sort_by?: string;
  limit?: number;
  offset?: number;
}

export interface RadiusSearchParams extends SpatialFilterParams {
  latitude: number;
  longitude: number;
  radius_km?: number;
}

export interface BoundingBoxSearchParams extends SpatialFilterParams {
  min_lat: number;
  min_lng: number;
  max_lat: number;
  max_lng: number;
}

export interface ViewportSearchParams extends SpatialFilterParams {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface PolygonSearchParams extends SpatialFilterParams {
  polygon: {
    type: "Polygon";
    coordinates: number[][][];
  };
}

export interface PropertyWithDistance {
  property: Property;
  distance_km: number;
}

export interface RadiusSearchResponse {
  items: PropertyWithDistance[];
  total: number;
  center: {
    latitude: number;
    longitude: number;
  };
  radius_km: number;
}

export interface GeoJSONPointFeature {
  type: "Feature";
  id?: number;
  geometry: {
    type: "Point";
    coordinates: [number, number]; // [lng, lat]
  };
  properties: {
    id: number;
    title: string;
    price: number;
    property_type: string;
    bedrooms?: number | null;
    bathrooms?: number | null;
    area_sqft: number;
    locality: string;
    city: string;
    status: string;
    primary_image?: string | null;
    distance_km?: number;
    [key: string]: unknown;
  };
}

export interface GeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: GeoJSONPointFeature[];
  total?: number;
}

export interface MapBounds {
  north: number;
  south: number;
  east: number;
  west: number;
}

export interface MapViewportState {
  latitude: number;
  longitude: number;
  zoom: number;
  bearing?: number;
  pitch?: number;
  bounds?: MapBounds;
}

// ==========================================
// API Error & System Responses
// ==========================================

export interface BackendErrorDetails {
  code: string;
  message: string;
  details?: unknown;
  request_id?: string;
}

export interface BackendErrorResponse {
  error: BackendErrorDetails;
}

export class APIError extends Error {
  code: string;
  statusCode: number;
  details?: unknown;
  requestId?: string;

  constructor(
    message: string,
    code = "UNKNOWN_ERROR",
    statusCode = 500,
    details?: unknown,
    requestId?: string
  ) {
    super(message);
    this.name = "APIError";
    this.code = code;
    this.statusCode = statusCode;
    this.details = details;
    this.requestId = requestId;
  }
}

// ==========================================
// POI Domain Types — Phase 7
// ==========================================

/**
 * Controlled vocabulary for Point of Interest categories.
 * Must stay in sync with backend POICategory enum.
 */
export type POICategory =
  | "hospital"
  | "school"
  | "transit"
  | "supermarket"
  | "park"
  | "pharmacy"
  | "bank";

/** All valid POI category values. Useful for filter UI iteration. */
export const POI_CATEGORIES: POICategory[] = [
  "hospital",
  "school",
  "transit",
  "supermarket",
  "park",
  "pharmacy",
  "bank",
];

/** Human-readable labels for POI categories. */
export const POI_CATEGORY_LABELS: Record<POICategory, string> = {
  hospital: "Hospitals",
  school: "Schools",
  transit: "Transit",
  supermarket: "Supermarkets",
  park: "Parks",
  pharmacy: "Pharmacies",
  bank: "Banks",
};

/** Point of Interest as returned by the backend API. */
export interface POI {
  id: number;
  name: string;
  category: POICategory;
  subcategory?: string | null;
  latitude: number;
  longitude: number;
  address?: string | null;
  city: string;
  locality?: string | null;
  is_active: boolean;
  created_at: string;
}

/** POI paired with a computed distance from a reference point. */
export interface POIWithDistance {
  poi: POI;
  distance_km: number;
}

/** Response envelope for nearby POI queries (/pois/nearby, /properties/{id}/nearby). */
export interface NearbyPOIsResponse {
  items: POIWithDistance[];
  total: number;
  radius_km: number;
  category: POICategory | null;
}

/** Location intelligence for a single category relative to a property. */
export interface CategoryIntelligence {
  /** Distance in km to nearest POI of this category. Null if no POI exists. */
  nearest_distance_km: number | null;
  /** Count of active POIs of this category within the search radius. */
  count_within_radius: number;
}

/** Full location intelligence summary for a property (all categories). */
export interface LocationIntelligenceResponse {
  property_id: number;
  radius_km: number;
  /** Keys are POICategory values. */
  categories: Partial<Record<POICategory, CategoryIntelligence>>;
}

/** GeoJSON Feature for a POI (RFC 7946). */
export interface POIGeoJSONFeature {
  type: "Feature";
  id: number;
  geometry: {
    type: "Point";
    coordinates: [number, number]; // [longitude, latitude]
  };
  properties: {
    id: number;
    name: string;
    category: POICategory;
    subcategory?: string | null;
    locality?: string | null;
    city: string;
    is_active: boolean;
  };
}

/** GeoJSON FeatureCollection for POI map queries (/maps/pois). */
export interface POIGeoJSONFeatureCollection {
  type: "FeatureCollection";
  features: POIGeoJSONFeature[];
  total: number;
}

/** Parameters for nearby POI search (/api/v1/pois/nearby). */
export interface NearbyPOIParams {
  latitude: number;
  longitude: number;
  radius_km?: number;
  category?: POICategory | null;
  limit?: number;
}

/** Parameters for map POI viewport query (/api/v1/maps/pois). */
export interface MapPOIParams {
  north: number;
  south: number;
  east: number;
  west: number;
  category?: POICategory | null;
  limit?: number;
}

/** Parameters for property-relative nearby POI query. */
export interface PropertyNearbyPOIParams {
  category?: POICategory | null;
  radius_km?: number;
  limit?: number;
}

// ==========================================
// Phase 8: Commute & Travel Intelligence Types
// ==========================================

export type TravelMode = "driving" | "walking" | "cycling" | "bicycling" | "transit";
export const TravelMode = {
  DRIVING: "driving" as const,
  WALKING: "walking" as const,
  CYCLING: "cycling" as const,
  BICYCLING: "bicycling" as const,
  TRANSIT: "transit" as const,
};
export type FactorWeights = RankingWeights;

export interface RouteGeometry {
  type: "LineString";
  coordinates: [number, number][]; // [longitude, latitude]
}

export interface CommuteOrigin {
  latitude: number;
  longitude: number;
}

export interface CommuteDestination {
  name: string;
  latitude: number;
  longitude: number;
}

export interface CommuteResponse {
  property_id?: number | null;
  origin: CommuteOrigin;
  destination: CommuteDestination;
  mode: TravelMode;
  distance_meters: number;
  distance_km: number;
  duration_seconds: number;
  duration_minutes: number;
  geometry: RouteGeometry;
  summary?: string | null;
  provider: string;
  cached: boolean;
}

export interface BatchCommuteRequest {
  destinations: CommuteDestination[];
  mode?: TravelMode;
}

export interface BatchCommuteResponse {
  property_id: number;
  origin: CommuteOrigin;
  mode: TravelMode;
  results: CommuteResponse[];
  total_destinations: number;
}

export interface CommuteCompareRequest {
  property_ids: number[];
  destination: CommuteDestination;
  mode?: TravelMode;
}

export interface CommuteCompareResponse {
  destination: CommuteDestination;
  mode: TravelMode;
  comparisons: CommuteResponse[];
  fastest_property_id?: number | null;
  shortest_property_id?: number | null;
}

export interface CommuteQueryParams {
  destination_lat: number;
  destination_lng: number;
  destination_name?: string;
  mode?: TravelMode;
}

// ==========================================
// Phase 9: Deterministic Ranking Types
// ==========================================

export interface RankingWeights {
  price?: number;
  bedrooms?: number;
  area?: number;
  location?: number;
  commute?: number;
  locality?: number;
}

export interface FactorScoreDetail {
  score: number;
  weight: number;
  weighted_contribution: number;
  available: boolean;
  description?: string | null;
  raw_value?: number | null;
}

export interface RankedPropertyItem {
  rank: number;
  property: Property;
  final_score: number;
  score_breakdown: Record<string, FactorScoreDetail>;
  commute_duration_minutes?: number | null;
  explanations: string[];
}

export interface RankingConfigResponse {
  algorithm_version: string;
  weights: RankingWeights;
  candidate_pool_size: number;
}

export interface RankedSearchRequest {
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
  bathrooms?: number;
  property_type?: string;
  city?: string;
  locality?: string;
  status?: string;

  // Spatial constraints
  center_lat?: number;
  center_lng?: number;
  radius_km?: number;
  min_lat?: number;
  max_lat?: number;
  min_lng?: number;
  max_lng?: number;

  // Soft preferences
  target_price?: number;
  preferred_bedrooms?: number;
  min_area_sqft?: number;
  preferred_locality?: string;
  preferred_poi_categories?: POICategory[];
  destination?: CommuteDestination;
  travel_mode?: TravelMode;
  weights?: RankingWeights;

  limit?: number;
  offset?: number;
}

export interface RankedSearchResponse {
  total_candidates: number;
  ranking_config: RankingConfigResponse;
  items: RankedPropertyItem[];
  page: number;
  page_size: number;
  total_pages: number;
}

// ==========================================
// Phase 11: AI Integration Types
// ==========================================
export * from "./ai";

// ==========================================
// Phase 13: Grounded Comparison Types
// ==========================================
export * from "./comparison";

// ==========================================
// Phase 14: Conversational Search Types
// ==========================================
export * from "./conversational_search";
