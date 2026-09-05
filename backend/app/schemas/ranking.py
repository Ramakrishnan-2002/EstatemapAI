from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.poi_category import POICategory
from app.schemas.commute import CommuteDestination
from app.schemas.property import PropertyResponse
from app.services.routing.models import TravelMode


class RankingWeights(BaseModel):
    """
    Configurable weights for the deterministic ranking algorithm.
    All weights must be non-negative, and their sum must be strictly positive.
    """

    price: float = Field(
        default=0.25, ge=0.0, description="Affordability / budget adherence weight."
    )
    bedrooms: float = Field(default=0.20, ge=0.0, description="Bedroom requirement match weight.")
    area: float = Field(default=0.10, ge=0.0, description="Living area / size match weight.")
    location: float = Field(
        default=0.20, ge=0.0, description="POI proximity / location intelligence weight."
    )
    commute: float = Field(
        default=0.25, ge=0.0, description="Commute convenience & travel time weight."
    )
    locality: float = Field(
        default=0.00, ge=0.0, description="Specific neighborhood / locality match weight."
    )

    @model_validator(mode="after")
    def validate_sum_positive(self) -> RankingWeights:
        total = (
            self.price + self.bedrooms + self.area + self.location + self.commute + self.locality
        )
        if total <= 0.0:
            raise ValueError("The sum of ranking weights must be strictly greater than 0.")
        return self

    def normalize(self) -> dict[str, float]:
        """Return a dictionary of weights normalized so that their sum equals 1.0."""
        total = (
            self.price + self.bedrooms + self.area + self.location + self.commute + self.locality
        )
        return {
            "price": self.price / total,
            "bedrooms": self.bedrooms / total,
            "area": self.area / total,
            "location": self.location / total,
            "commute": self.commute / total,
            "locality": self.locality / total,
        }


class FactorScoreDetail(BaseModel):
    """Granular score breakdown for an individual ranking criterion."""

    score: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized factor score in range [0.0, 1.0]."
    )
    weight: float = Field(
        ..., ge=0.0, le=1.0, description="Normalized weight assigned to this factor."
    )
    weighted_contribution: float = Field(
        ..., ge=0.0, le=100.0, description="Contribution to final score (score * weight * 100)."
    )
    available: bool = Field(
        True, description="Whether authoritative data was available to evaluate this factor."
    )
    description: str | None = Field(
        None, description="Factual description or metric value for this factor."
    )
    raw_value: float | None = Field(
        None, description="Authoritative numeric measurement (e.g. commute duration in minutes)."
    )


class RankedPropertyItem(BaseModel):
    """An eligible property evaluated, scored, and ordered by the ranking engine."""

    model_config = ConfigDict(from_attributes=True)

    rank: int = Field(..., ge=1, description="1-based ordinal rank among eligible candidates.")
    property: PropertyResponse
    final_score: float = Field(
        ..., ge=0.0, le=100.0, description="Final deterministic match score in range [0.0, 100.0]."
    )
    score_breakdown: dict[str, FactorScoreDetail] = Field(
        ..., description="Per-factor score details and contributions."
    )
    commute_duration_minutes: float | None = Field(
        default=None,
        description="Authoritative numeric commute duration in minutes, if evaluated.",
    )
    explanations: list[str] = Field(
        default_factory=list, description="Deterministic rule-based factual explanation bullets."
    )


class RankingConfigResponse(BaseModel):
    """Identifies the ranking algorithm version and active weight configuration."""

    algorithm_version: str = Field(..., description="Deterministic ranking algorithm identifier.")
    weights: RankingWeights
    candidate_pool_size: int = Field(
        ..., description="Number of eligible candidates retrieved from hard filtering."
    )


class RankedSearchRequest(BaseModel):
    """
    Unified payload combining hard database filtering constraints
    and deterministic soft ranking preferences.
    """

    # --- Hard Database Filters ---
    min_price: float | None = Field(default=None, ge=0.0, description="Minimum price filter.")
    max_price: float | None = Field(default=None, ge=0.0, description="Maximum price filter.")
    bedrooms: int | None = Field(default=None, ge=0, description="Hard bedroom count filter.")
    bathrooms: float | None = Field(
        default=None, ge=0.0, description="Minimum bathroom count filter."
    )
    property_type: str | None = Field(default=None, description="Property type filter.")
    city: str | None = Field(default=None, description="City filter.")
    locality: str | None = Field(default=None, description="Locality filter.")
    status: str = Field(default="active", description="Property listing status filter.")

    # --- Spatial Hard Constraints (Optional) ---
    # Radius constraint
    center_lat: float | None = Field(default=None, ge=-90.0, le=90.0)
    center_lng: float | None = Field(default=None, ge=-180.0, le=180.0)
    radius_km: float | None = Field(default=None, gt=0.0, le=200.0)

    # Bounding box constraint
    min_lat: float | None = Field(default=None, ge=-90.0, le=90.0)
    max_lat: float | None = Field(default=None, ge=-90.0, le=90.0)
    min_lng: float | None = Field(default=None, ge=-180.0, le=180.0)
    max_lng: float | None = Field(default=None, ge=-180.0, le=180.0)

    # --- Soft Ranking Preferences ---
    target_price: float | None = Field(
        default=None, ge=0.0, description="Ideal budget for affordability scoring."
    )
    preferred_bedrooms: int | None = Field(
        default=None, ge=0, description="Preferred bedroom count for soft scoring."
    )
    min_area_sqft: float | None = Field(
        default=None, ge=0.0, description="Preferred minimum area in sq ft."
    )
    preferred_locality: str | None = Field(
        default=None, description="Preferred locality name for locality scoring."
    )
    preferred_poi_categories: list[POICategory] | None = Field(
        default=None,
        description="Key POI categories prioritized for location intelligence scoring.",
    )
    destination: CommuteDestination | None = Field(
        default=None,
        description="Workplace or reference destination for commute travel time scoring.",
    )
    travel_mode: TravelMode = Field(
        default=TravelMode.DRIVING,
        description="Travel mode for commute calculation.",
    )
    weights: RankingWeights = Field(
        default_factory=RankingWeights,
        description="Configurable factor weights. Sum of weights must be > 0.",
    )

    # --- Pagination ---
    limit: int = Field(
        default=10, ge=1, le=50, description="Number of ranked items to return per page."
    )
    offset: int = Field(default=0, ge=0, description="Pagination offset.")


class RankedSearchResponse(BaseModel):
    """Complete ranked search response containing ordered properties, score breakdowns, and metadata."""

    total_candidates: int = Field(
        ..., description="Total eligible properties found after hard filtering."
    )
    ranking_config: RankingConfigResponse
    items: list[RankedPropertyItem] = Field(
        ..., description="Ranked property items ordered by score descending."
    )
    page: int
    page_size: int
    total_pages: int
