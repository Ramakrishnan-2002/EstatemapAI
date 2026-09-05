from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.poi_category import POICategory
from app.services.routing.models import TravelMode
from app.utils.price_parser import IndianPriceParser


class PropertySearchIntent(BaseModel):
    """
    Validated structured natural-language search intent extracted by the AI layer.
    Strictly constrained by domain bounds and Pydantic validation.
    """

    model_config = ConfigDict(use_enum_values=True)

    raw_query: str = Field(description="Original user natural language query")
    bedrooms: int | None = Field(
        default=None, ge=1, le=10, description="Desired number of bedrooms (1 to 10)"
    )
    bathrooms: float | None = Field(
        default=None, ge=1.0, le=10.0, description="Desired number of bathrooms (1.0 to 10.0)"
    )
    min_price: float | None = Field(default=None, ge=0.0, description="Minimum price in INR")
    max_price: float | None = Field(default=None, ge=0.0, description="Maximum price in INR")
    min_area_sqft: float | None = Field(
        default=None, ge=50.0, le=100000.0, description="Minimum carpet area in sqft"
    )
    property_type: str | None = Field(
        default=None, description="Property type (e.g. apartment, villa, penthouse)"
    )
    locality: str | None = Field(
        default=None, description="Preferred locality or neighborhood name"
    )
    city: str | None = Field(default=None, description="Target city name")
    preferred_poi_categories: list[POICategory] = Field(
        default_factory=list,
        description="List of requested nearby POI categories (e.g. hospital, school, metro)",
    )
    commute_destination: str | None = Field(
        default=None, description="Key commute workplace/destination mentioned by the user"
    )
    confidence: float = Field(
        default=1.0,
        ge=0.0,
        le=1.0,
        description="AI extraction confidence score between 0.0 and 1.0",
    )

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, val: Any) -> float:
        if val is None:
            return 1.0
        try:
            f = float(val)
            return max(0.0, min(1.0, f))
        except (ValueError, TypeError):
            return 1.0

    @field_validator("min_price", "max_price", mode="before")
    @classmethod
    def normalize_price(cls, val: Any) -> float | None:
        if val is None:
            return None
        if isinstance(val, int | float):
            if val < 0:
                raise ValueError("Price cannot be negative")
            return float(val)
        parsed = IndianPriceParser.parse_inr(str(val))
        if parsed is not None and parsed < 0:
            raise ValueError("Price cannot be negative")
        return parsed

    @field_validator("preferred_poi_categories", mode="before")
    @classmethod
    def normalize_poi_categories(cls, val: Any) -> list[Any]:
        if not val:
            return []
        if isinstance(val, str):
            val = [val]
        valid = []
        for item in val:
            if isinstance(item, POICategory):
                valid.append(item)
            elif isinstance(item, str):
                cleaned = item.strip().lower().replace(" ", "_").replace("-", "_")
                # Map common colloquial category synonyms
                synonym_map = {
                    "metro": "transit",
                    "bus_stand": "transit",
                    "transit_station": "transit",
                    "train_station": "transit",
                    "train": "transit",
                    "market": "supermarket",
                    "grocery": "supermarket",
                    "clinic": "hospital",
                    "healthcare": "hospital",
                    "college": "school",
                    "university": "school",
                    "dining": "restaurant",
                    "cafe": "restaurant",
                    "fitness": "gym",
                    "atm": "bank",
                }
                cleaned = synonym_map.get(cleaned, cleaned)
                try:
                    valid.append(POICategory(cleaned))
                except ValueError:
                    continue
        return valid

    @model_validator(mode="after")
    def validate_price_range(self) -> PropertySearchIntent:
        if self.min_price is not None and self.max_price is not None:
            if self.min_price > self.max_price:
                # Swap or clamp if inverted
                self.min_price, self.max_price = self.max_price, self.min_price
        return self


# Backward-compatible alias for existing imports
ParsedSearchIntent = PropertySearchIntent


class AIUsageMetadata(BaseModel):
    """Token usage metadata for AI generation calls."""

    input_tokens: int | None = Field(default=None, description="Number of prompt/input tokens")
    output_tokens: int | None = Field(
        default=None, description="Number of completion/output tokens"
    )
    total_tokens: int | None = Field(default=None, description="Total tokens consumed")


class ParseSearchRequest(BaseModel):
    query: str = Field(
        min_length=3,
        max_length=500,
        description="Natural language search query (e.g. '2 BHK under 70 lakh near Whitefield with hospital access')",
    )


class ParseSearchResponse(BaseModel):
    provider: str
    model: str
    intent: PropertySearchIntent
    latency_ms: float
    prompt_version: str
    fallback_used: bool = False
    routing_reason: str | None = None
    usage: AIUsageMetadata | None = None


class AIExplanationRequest(BaseModel):
    destination_lat: float | None = Field(
        default=None, ge=-90.0, le=90.0, description="Optional commute destination latitude"
    )
    destination_lng: float | None = Field(
        default=None, ge=-180.0, le=180.0, description="Optional commute destination longitude"
    )
    destination_name: str | None = Field(
        default=None, description="Optional commute destination label (e.g. 'Office')"
    )
    travel_mode: TravelMode = Field(
        default=TravelMode.DRIVING, description="Travel mode for commute calculation"
    )


class AIExplanationResponse(BaseModel):
    property_id: int
    explanation: str
    provider: str
    model: str
    latency_ms: float
    fallback_used: bool = False
    factual_context: dict[str, Any]
    prompt_version: str
    routing_reason: str | None = None
    usage: AIUsageMetadata | None = None


class ProviderHealthDetail(BaseModel):
    """Detailed health probe for an individual AI provider."""

    model_config = ConfigDict(protected_namespaces=())

    configured: bool = True
    reachable: bool = False
    model: str
    model_available: bool = False
    available_models: list[str] = Field(default_factory=list)
    latency_ms: float | None = None
    authenticated: bool | None = None
    error: str | None = None


class AIHealthResponse(BaseModel):
    """Unified multi-provider health response."""

    model_config = ConfigDict(protected_namespaces=())

    enabled: bool
    configured_provider: str = "auto"
    active_primary: str = "ollama"
    provider: str = "ollama"  # Backward-compatible alias
    reachable: bool
    model: str
    model_available: bool
    available_models: list[str] = Field(default_factory=list)
    latency_ms: float | None = None
    providers: dict[str, ProviderHealthDetail] = Field(default_factory=dict)
    details: dict[str, Any] | None = None
