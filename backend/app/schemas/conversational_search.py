from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.poi_category import POICategory
from app.schemas.comparison import ComparisonResult
from app.schemas.geo import BoundingBoxSearchParams
from app.schemas.ranking import RankedPropertyItem, RankedSearchResponse, RankingWeights
from app.services.routing.models import TravelMode
from app.utils.price_parser import IndianPriceParser


class ConversationAction(StrEnum):
    """
    Bounded set of allowed actions supported by the conversational search orchestrator.
    """

    SEARCH = "search"
    REFINE = "refine"
    CLEAR_FILTER = "clear_filter"
    RESET_SEARCH = "reset_search"
    RANK = "rank"
    COMPARE = "compare"
    EXPLAIN = "explain"


class AllowedSearchField(StrEnum):
    """
    Allowed filter field keys for explicit clear/reset operations.
    """

    PRICE = "price"
    MIN_PRICE = "min_price"
    MAX_PRICE = "max_price"
    BEDROOMS = "bedrooms"
    BATHROOMS = "bathrooms"
    MIN_AREA_SQFT = "min_area_sqft"
    PROPERTY_TYPE = "property_type"
    LOCALITY = "locality"
    CITY = "city"
    POI_CATEGORIES = "preferred_poi_categories"
    COMMUTE = "commute"
    COMMUTE_DESTINATION = "commute_destination"
    MAX_COMMUTE_MINUTES = "max_commute_minutes"
    RANKING = "ranking"
    VIEWPORT = "viewport"


class ConversationalSearchState(BaseModel):
    """
    Authoritative canonical search state shared between manual UI controls
    and multi-turn conversational refinements.
    """

    model_config = ConfigDict(use_enum_values=True)

    # Core hard filters
    min_price: float | None = Field(
        default=None, ge=0.0, description="Minimum price filter in INR."
    )
    max_price: float | None = Field(
        default=None, ge=0.0, description="Maximum price filter in INR."
    )
    bedrooms: int | None = Field(
        default=None, ge=1, le=10, description="Exact or minimum bedroom count (1 to 10)."
    )
    bathrooms: float | None = Field(
        default=None, ge=1.0, le=10.0, description="Minimum bathroom count."
    )
    min_area_sqft: float | None = Field(
        default=None, ge=50.0, description="Minimum carpet area in sqft."
    )
    property_type: str | None = Field(
        default=None, description="Property type (e.g. apartment, villa, penthouse, plot)."
    )
    city: str | None = Field(default=None, description="City name (e.g. Bengaluru).")
    locality: str | None = Field(default=None, description="Locality / neighborhood name.")

    # Location intelligence & POIs
    preferred_poi_categories: list[POICategory] = Field(
        default_factory=list,
        description="POI categories of interest (e.g. hospital, school, transit, park, supermarket).",
    )

    # Commute travel intelligence
    commute_destination: str | None = Field(
        default=None, description="Name or label of the commute workplace / destination."
    )
    destination_lat: float | None = Field(
        default=None, ge=-90.0, le=90.0, description="Verified destination latitude."
    )
    destination_lng: float | None = Field(
        default=None, ge=-180.0, le=180.0, description="Verified destination longitude."
    )
    travel_mode: TravelMode = Field(
        default=TravelMode.DRIVING, description="Travel mode for commute calculation."
    )
    max_commute_minutes: float | None = Field(
        default=None, ge=1.0, le=180.0, description="Hard cap on commute travel time in minutes."
    )

    # Geospatial viewport & radius
    viewport_bbox: BoundingBoxSearchParams | None = Field(
        default=None, description="Current map bounding box viewport constraint."
    )
    radius_km: float | None = Field(
        default=None, ge=0.1, le=50.0, description="Radius distance in km."
    )

    # Deterministic ranking configuration
    ranking_preset: str = Field(
        default="balanced",
        description="Active ranking preset (balanced, budget_first, commute_first, space_first, amenity_focused).",
    )
    ranking_weights: RankingWeights = Field(
        default_factory=RankingWeights,
        description="Active preference weights for deterministic scoring.",
    )

    # Selected property IDs for comparison
    selected_property_ids: list[int] = Field(
        default_factory=list,
        max_length=3,
        description="Property IDs currently staged for multi-property comparison.",
    )


class SearchStatePatch(BaseModel):
    """
    Validated state patch extracted by AI from a user's natural-language message.
    Represents an atomic mutation applied to ConversationalSearchState.
    """

    model_config = ConfigDict(use_enum_values=True)

    # Fields to set / replace
    min_price: float | None = Field(default=None, ge=0.0)
    max_price: float | None = Field(default=None, ge=0.0)
    bedrooms: int | None = Field(default=None, ge=1, le=10)
    bathrooms: float | None = Field(default=None, ge=1.0, le=10.0)
    min_area_sqft: float | None = Field(default=None, ge=50.0)
    property_type: str | None = None
    city: str | None = None
    locality: str | None = None

    # POI mutations
    add_poi_categories: list[POICategory] = Field(default_factory=list)
    remove_poi_categories: list[POICategory] = Field(default_factory=list)

    # Commute mutations
    commute_destination: str | None = None
    travel_mode: TravelMode | None = None
    max_commute_minutes: float | None = Field(default=None, ge=1.0, le=180.0)

    # Ranking mutations
    ranking_preset: str | None = Field(
        default=None,
        description="Preset identifier (budget_first, commute_first, space_first, amenity_focused, balanced).",
    )

    # Explicit fields to clear
    clear_fields: list[AllowedSearchField] = Field(
        default_factory=list,
        description="List of fields to explicitly remove/reset from state.",
    )

    # High-level action requested
    requested_action: ConversationAction = Field(
        default=ConversationAction.REFINE,
        description="Interpreted intent action.",
    )

    # Comparison / Explanation targets
    target_property_indices: list[int] = Field(
        default_factory=list,
        description="1-based property rank positions targeted for compare or explain (e.g. [1, 2] for 'top two').",
    )

    confidence: float = Field(default=1.0, ge=0.0, le=1.0)

    @field_validator("target_property_indices", mode="before")
    @classmethod
    def normalize_target_indices(cls, val: Any) -> list[int]:
        if val is None:
            return []
        if isinstance(val, list):
            return [int(x) for x in val if str(x).isdigit()]
        if isinstance(val, int | str) and str(val).isdigit():
            return [int(val)]
        return []

    @field_validator("clear_fields", mode="before")
    @classmethod
    def normalize_clear_fields(cls, val: Any) -> list[Any]:
        if val is None:
            return []
        if isinstance(val, list):
            return val
        return [val]

    @field_validator("requested_action", mode="before")
    @classmethod
    def normalize_requested_action(cls, val: Any) -> Any:
        if val is None or val == "":
            return ConversationAction.SEARCH
        return val

    @field_validator("confidence", mode="before")
    @classmethod
    def normalize_confidence(cls, val: Any) -> float:
        if val is None:
            return 1.0
        try:
            c = float(val)
            return max(0.0, min(1.0, c))
        except Exception:
            return 1.0

    @field_validator("min_price", "max_price", mode="before")
    @classmethod
    def normalize_price_val(cls, val: Any) -> float | None:
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

    @field_validator("add_poi_categories", "remove_poi_categories", mode="before")
    @classmethod
    def normalize_pois(cls, val: Any) -> list[Any]:
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
                synonym_map = {
                    "metro": "transit",
                    "bus_stand": "transit",
                    "transit_station": "transit",
                    "train_station": "transit",
                    "train": "transit",
                    "market": "supermarket",
                    "grocery": "supermarket",
                    "clinic": "hospital",
                    "greenery": "park",
                    "garden": "park",
                    "playground": "park",
                }
                mapped = synonym_map.get(cleaned, cleaned)
                try:
                    valid.append(POICategory(mapped))
                except ValueError:
                    pass
        return valid


class AskMapRequest(BaseModel):
    """
    Request payload for multi-turn conversational property discovery.
    """

    model_config = ConfigDict(use_enum_values=True)

    message: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="User natural-language search query or conversational refinement.",
    )
    session_id: str | None = Field(
        default=None,
        description="Optional client session identifier for conversation continuity.",
    )
    current_state: ConversationalSearchState = Field(
        default_factory=ConversationalSearchState,
        description="Current canonical structured search state.",
    )
    map_viewport: BoundingBoxSearchParams | None = Field(
        default=None,
        description="Current map viewport bounding box.",
    )


class AppliedPatchFeedback(BaseModel):
    """
    Deterministic breakdown of what changed in the search state after applying a patch.
    """

    added: list[str] = Field(
        default_factory=list, description="Descriptions of newly applied constraints."
    )
    modified: list[str] = Field(
        default_factory=list, description="Descriptions of altered criteria."
    )
    removed: list[str] = Field(default_factory=list, description="Descriptions of cleared filters.")
    preserved: list[str] = Field(
        default_factory=list, description="Descriptions of retained criteria."
    )


class AskMapResponse(BaseModel):
    """
    Complete orchestration response returned by POST /api/v1/ai/ask-map.
    Provides updated structured state, human-readable feedback, search results,
    GeoJSON map data, and optional comparison/explanation artifacts.
    """

    model_config = ConfigDict(use_enum_values=True)

    session_id: str | None = None
    message: str = Field(description="Clear, concise natural-language feedback message.")
    action: ConversationAction = Field(
        description="Authoritative action executed by the orchestrator."
    )
    state: ConversationalSearchState = Field(
        description="Updated authoritative canonical search state."
    )
    applied_patch: SearchStatePatch | None = None
    feedback: AppliedPatchFeedback = Field(default_factory=AppliedPatchFeedback)

    # Search & ranking results
    ranked_search_response: RankedSearchResponse | None = None
    items: list[RankedPropertyItem] = Field(default_factory=list)
    total_matches: int = 0
    map_geojson: dict[str, Any] = Field(
        default_factory=dict, description="RFC 7946 FeatureCollection."
    )

    # Dedicated action payloads
    comparison_result: ComparisonResult | None = None
    explanation_bullets: list[str] = Field(default_factory=list)

    # Clarification & safety flags
    needs_clarification: bool = False
    clarification_prompt: str | None = None

    # Telemetry
    provider: str = "orchestrator"
    model: str = "deterministic"
    latency_ms: float = 0.0
    fallback_used: bool = False
    routing_reason: str | None = None
