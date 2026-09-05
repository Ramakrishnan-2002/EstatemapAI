import { POICategory, TravelMode, FactorWeights, FactorScoreDetail } from './index';
import { AIUsageMetadata } from './ai';

export interface PropertyComparisonRequest {
  property_ids: number[];
  destination_lat?: number | null;
  destination_lng?: number | null;
  destination_name?: string | null;
  travel_mode?: TravelMode;
  target_price?: number | null;
  preferred_bedrooms?: number | null;
  min_area_sqft?: number | null;
  preferred_locality?: string | null;
  preferred_poi_categories?: POICategory[];
  weights?: FactorWeights;
}

export interface PropertyComparisonFact {
  id: number;
  label: string; // "Property A", "Property B", "Property C"
  title: string;
  price: number;
  price_formatted: string;
  price_per_sqft?: number | null;
  bedrooms?: number | null;
  bathrooms?: number | null;
  area_sqft?: number | null;
  property_type: string;
  address: string;
  locality: string;
  city: string;
  latitude: number;
  longitude: number;
  image_urls: string[];
  location_intelligence: Record<string, number | null>;
  commute_duration_mins?: number | null;
  commute_distance_km?: number | null;
  commute_destination?: string | null;
  ranking_score?: number | null;
  score_breakdown: Record<string, FactorScoreDetail>;
}

export interface ComparisonDimensionSummary {
  dimension: string;
  best_property_label?: string | null;
  best_metric_label?: string | null;
  metric_name: string;
  details: Record<string, any>;
  comparison_notes: string[];
}

export interface RankingContributionDelta {
  winner_label: string;
  loser_label: string;
  winner_score: number;
  loser_score: number;
  net_score_delta: number;
  factor_deltas: Record<string, number>;
  summary: string;
}

export interface ComparisonResult {
  properties: PropertyComparisonFact[];
  dimensions: Record<string, ComparisonDimensionSummary>;
  ranking_deltas: RankingContributionDelta[];
  deterministic_summary: string[];
  best_by_dimension: Record<string, string | null>;
}

export interface AIComparisonResponse {
  property_ids: number[];
  narrative: string;
  comparison: ComparisonResult;
  provider: string;
  model: string;
  latency_ms: number;
  fallback_used: boolean;
  prompt_version: string;
  routing_reason?: string | null;
  usage?: AIUsageMetadata | null;
}
