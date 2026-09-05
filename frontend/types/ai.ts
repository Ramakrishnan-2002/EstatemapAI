import { POICategory, TravelMode } from './index';

export interface PropertySearchIntent {
  raw_query: string;
  bedrooms?: number | null;
  bathrooms?: number | null;
  min_price?: number | null;
  max_price?: number | null;
  min_area_sqft?: number | null;
  property_type?: string | null;
  locality?: string | null;
  city?: string | null;
  preferred_poi_categories: POICategory[];
  commute_destination?: string | null;
  confidence: number;
}

export interface AIUsageMetadata {
  input_tokens?: number | null;
  output_tokens?: number | null;
  total_tokens?: number | null;
}

export interface ParseSearchRequest {
  query: string;
}

export interface ParseSearchResponse {
  provider: string;
  model: string;
  intent: PropertySearchIntent;
  latency_ms: number;
  prompt_version: string;
  fallback_used?: boolean;
  routing_reason?: string | null;
  usage?: AIUsageMetadata | null;
}

export interface AIExplanationRequest {
  destination_lat?: number | null;
  destination_lng?: number | null;
  destination_name?: string | null;
  travel_mode?: TravelMode;
}

export interface AIExplanationResponse {
  property_id: number;
  explanation: string;
  provider: string;
  model: string;
  latency_ms: number;
  fallback_used: boolean;
  factual_context: Record<string, any>;
  prompt_version: string;
  routing_reason?: string | null;
  usage?: AIUsageMetadata | null;
}

export interface ProviderHealthDetail {
  configured: boolean;
  reachable: boolean;
  model: string;
  model_available: boolean;
  available_models: string[];
  latency_ms?: number | null;
  authenticated?: boolean | null;
  error?: string | null;
}

export interface AIHealthResponse {
  enabled: boolean;
  configured_provider?: string;
  active_primary?: string;
  provider: string;
  reachable: boolean;
  model: string;
  model_available: boolean;
  available_models: string[];
  latency_ms?: number | null;
  providers?: Record<string, ProviderHealthDetail>;
  details?: Record<string, any> | null;
}
