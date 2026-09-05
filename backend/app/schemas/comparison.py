from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.poi_category import POICategory
from app.schemas.ai import AIUsageMetadata
from app.schemas.ranking import FactorScoreDetail, RankingWeights
from app.services.routing.models import TravelMode


class PropertyComparisonRequest(BaseModel):
    """
    Request payload to compare 2 to 3 properties deterministically.
    """

    model_config = ConfigDict(use_enum_values=True)

    property_ids: list[int] = Field(
        ...,
        min_length=2,
        max_length=3,
        description="List of 2 to 3 distinct property IDs to compare.",
    )
    destination_lat: float | None = Field(
        default=None,
        ge=-90.0,
        le=90.0,
        description="Optional commute destination latitude (-90.0 to 90.0).",
    )
    destination_lng: float | None = Field(
        default=None,
        ge=-180.0,
        le=180.0,
        description="Optional commute destination longitude (-180.0 to 180.0).",
    )
    destination_name: str | None = Field(
        default=None,
        max_length=150,
        description="Optional commute destination label (e.g. 'Office - Electronic City').",
    )
    travel_mode: TravelMode = Field(
        default=TravelMode.DRIVING,
        description="Travel mode for commute calculation.",
    )
    weights: RankingWeights = Field(
        default_factory=RankingWeights,
        description="Configurable preference weights for ranking match scores.",
    )
    preferred_bedrooms: int | None = Field(
        default=None, ge=1, le=10, description="Preferred bedroom requirement."
    )
    preferred_locality: str | None = Field(
        default=None, description="Preferred locality for score evaluation."
    )
    preferred_poi_categories: list[POICategory] = Field(
        default_factory=list, description="Preferred POI categories for location score."
    )
    target_price: float | None = Field(
        default=None, ge=0.0, description="Target budget price for scoring."
    )
    min_area_sqft: float | None = Field(
        default=None, ge=50.0, description="Minimum carpet area requirement in sqft."
    )

    @field_validator("property_ids")
    @classmethod
    def validate_property_ids(cls, v: list[int]) -> list[int]:
        if len(v) < 2:
            raise ValueError("At least 2 property IDs are required for comparison.")
        if len(v) > 3:
            raise ValueError("At most 3 property IDs can be compared simultaneously.")
        if len(set(v)) != len(v):
            raise ValueError("Duplicate property IDs in comparison request are not allowed.")
        return v

    @model_validator(mode="after")
    def validate_destination(self) -> PropertyComparisonRequest:
        if (self.destination_lat is not None and self.destination_lng is None) or (
            self.destination_lat is None and self.destination_lng is not None
        ):
            raise ValueError("Both destination_lat and destination_lng must be provided together.")
        return self


class PropertyComparisonFact(BaseModel):
    """
    Authoritative factual snapshot of an individual property in a comparison.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    label: str = Field(description="Generic comparison label (Property A, Property B, Property C)")
    title: str
    price: float
    price_formatted: str
    price_per_sqft: float | None = None
    bedrooms: int | None = None
    bathrooms: float | None = None
    area_sqft: float | None = None
    property_type: str
    address: str
    locality: str
    city: str
    latitude: float
    longitude: float
    image_urls: list[str] = Field(default_factory=list)
    location_intelligence: dict[str, float | None] = Field(
        default_factory=dict,
        description="Nearest distance in km for key POI categories (e.g. hospital, school, transit).",
    )
    commute_duration_mins: float | None = None
    commute_distance_km: float | None = None
    commute_destination: str | None = None
    ranking_score: float | None = None
    score_breakdown: dict[str, FactorScoreDetail] = Field(default_factory=dict)


class ComparisonDimensionSummary(BaseModel):
    """
    Structured summary and relative comparison for a specific dimension (price, space, location, commute, ranking).
    """

    dimension: str
    best_property_label: str | None = None
    best_metric_label: str | None = None
    metric_name: str
    details: dict[str, Any] = Field(default_factory=dict)
    comparison_notes: list[str] = Field(default_factory=list)


class RankingContributionDelta(BaseModel):
    """
    Mathematical breakdown explaining why a higher-ranked property scored above a lower-ranked property.
    """

    winner_label: str
    loser_label: str
    winner_score: float
    loser_score: float
    net_score_delta: float
    factor_deltas: dict[str, float] = Field(
        default_factory=dict,
        description="Per-factor weighted contribution delta (winner_contrib - loser_contrib).",
    )
    summary: str


class ComparisonResult(BaseModel):
    """
    Deterministic comparison payload containing authoritative facts, dimension summaries,
    ranking contribution deltas, and preformatted factual explanation statements.
    """

    properties: list[PropertyComparisonFact]
    dimensions: dict[str, ComparisonDimensionSummary]
    ranking_deltas: list[RankingContributionDelta] = Field(default_factory=list)
    deterministic_summary: list[str] = Field(
        default_factory=list,
        description="Precomputed factual difference statements in Python to eliminate LLM arithmetic hallucination.",
    )
    best_by_dimension: dict[str, str | None] = Field(
        default_factory=dict,
        description="Mapping of dimension (price, space, commute, location, ranking) to winning property label.",
    )


class AIComparisonResponse(BaseModel):
    """
    Combined AI comparative response containing authoritative comparison data and natural-language narrative.
    """

    comparison: ComparisonResult
    narrative: str
    provider: str
    model: str
    latency_ms: float
    fallback_used: bool = False
    prompt_version: str
    routing_reason: str | None = None
    usage: AIUsageMetadata | None = None
