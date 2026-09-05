import { POICategory, Property, TravelMode, BoundingBoxSearchParams, ViewportSearchParams } from './index';
import { RankedPropertyItem, RankedSearchResponse, RankingWeights } from './index';
import { ComparisonResult } from './comparison';

export type ConversationAction =
  | 'search'
  | 'refine'
  | 'clear_filter'
  | 'reset_search'
  | 'rank'
  | 'compare'
  | 'explain';

export type AllowedSearchField =
  | 'price'
  | 'min_price'
  | 'max_price'
  | 'bedrooms'
  | 'bathrooms'
  | 'min_area_sqft'
  | 'property_type'
  | 'locality'
  | 'city'
  | 'preferred_poi_categories'
  | 'commute'
  | 'commute_destination'
  | 'max_commute_minutes'
  | 'ranking'
  | 'viewport';

export interface ConversationalSearchState {
  min_price?: number | null;
  max_price?: number | null;
  bedrooms?: number | null;
  bathrooms?: number | null;
  min_area_sqft?: number | null;
  property_type?: string | null;
  city?: string | null;
  locality?: string | null;
  preferred_poi_categories: POICategory[];
  commute_destination?: string | null;
  destination_lat?: number | null;
  destination_lng?: number | null;
  travel_mode: TravelMode;
  max_commute_minutes?: number | null;
  viewport_bbox?: BoundingBoxSearchParams | ViewportSearchParams | null;
  ranking_preset: string;
  ranking_weights: RankingWeights;
  selected_property_ids: number[];
}

export interface SearchStatePatch {
  min_price?: number | null;
  max_price?: number | null;
  bedrooms?: number | null;
  bathrooms?: number | null;
  min_area_sqft?: number | null;
  property_type?: string | null;
  city?: string | null;
  locality?: string | null;
  add_poi_categories?: POICategory[];
  remove_poi_categories?: POICategory[];
  commute_destination?: string | null;
  travel_mode?: TravelMode | null;
  max_commute_minutes?: number | null;
  ranking_preset?: string | null;
  clear_fields?: AllowedSearchField[];
  requested_action: ConversationAction;
  target_property_indices?: number[];
  confidence?: number;
}

export interface AppliedPatchFeedback {
  added: string[];
  modified: string[];
  removed: string[];
  preserved: string[];
}

export interface AskMapRequest {
  message: string;
  session_id?: string | null;
  current_state: ConversationalSearchState;
  map_viewport?: BoundingBoxSearchParams | ViewportSearchParams | null;
}

export interface AskMapResponse {
  session_id?: string | null;
  message: string;
  action: ConversationAction;
  state: ConversationalSearchState;
  applied_patch?: SearchStatePatch | null;
  feedback: AppliedPatchFeedback;
  ranked_search_response?: RankedSearchResponse | null;
  items: RankedPropertyItem[];
  total_matches: number;
  map_geojson: GeoJSON.FeatureCollection;
  comparison_result?: ComparisonResult | null;
  explanation_bullets?: string[];
  needs_clarification: boolean;
  clarification_prompt?: string | null;
  provider: string;
  model: string;
  latency_ms: number;
  fallback_used: boolean;
  routing_reason?: string | null;
}
