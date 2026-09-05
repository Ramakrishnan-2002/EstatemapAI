from __future__ import annotations

import re
from typing import Any

from pydantic import BaseModel, Field

from app.core.config import settings


class AIRequestProfile(BaseModel):
    """
    Measurable structural profile of an incoming AI operation used by deterministic routing rules.
    """

    operation: str = Field(description="Operation type: 'search_intent' or 'property_explanation'")
    query_length: int = Field(default=0, description="Character length of natural language input")
    core_filter_count: int = Field(
        default=0, description="Count of standard property filters (BHK, price, type, locality)"
    )
    poi_count: int = Field(default=0, description="Count of requested POI amenity categories")
    has_commute_target: bool = Field(
        default=False, description="Whether commute destination or travel time was detected"
    )
    has_multiple_pois: bool = Field(
        default=False, description="Whether 2 or more POI categories were requested"
    )
    complexity_score: int = Field(
        default=0, description="Deterministic integer complexity score computed by policy rules"
    )
    is_complex: bool = Field(
        default=False, description="Whether complexity_score >= AI_ROUTING_COMPLEXITY_THRESHOLD"
    )


class AIRoutingPolicy:
    """
    Deterministic rule-based policy engine for AI Provider selection and failover ordering.
    Core property filters alone stay with local Ollama; multi-dimensional context routes to Gemini.
    No LLM is ever used to choose the LLM.
    """

    @classmethod
    def profile_intent_query(cls, query: str) -> AIRequestProfile:
        """
        Analyze a search query and extract measurable structural heuristics.

        Scoring Rules:
        - Core property filters (BHK, price, type, area, locality): +1 total base score
        - Multiple POIs (>= 2 amenity categories): +2 points
        - Commute target / travel constraint: +2 points
        - Comparison or multi-clause expression: +2 points
        - Long natural language query (> 100 characters): +2 points

        A query is classified as complex if complexity_score >= AI_ROUTING_COMPLEXITY_THRESHOLD (default: 3).
        """
        q_lower = query.strip().lower()
        core_filter_count = 0
        has_commute = False
        poi_matches = 0
        is_comparison = False

        # 1. Bedroom indicators
        if re.search(r"\b(\d+)\s*(bhk|bed|bedroom|br)\b", q_lower) or any(
            w in q_lower for w in ["1bhk", "2bhk", "3bhk", "4bhk", "studio"]
        ):
            core_filter_count += 1

        # 2. Price indicators
        if re.search(r"\b(lakh|lakhs|lac|lacs|cr|crore|crores|k|thousand|₹|\$)\b", q_lower) or any(
            w in q_lower
            for w in ["under", "below", "max", "budget", "within", "upto", "above", "min"]
        ):
            core_filter_count += 1

        # 3. Property Type indicators
        if any(
            pt in q_lower
            for pt in ["apartment", "flat", "villa", "penthouse", "plot", "house", "independent"]
        ):
            core_filter_count += 1

        # 4. Area / sqft indicators
        if (
            re.search(r"\b(\d+)\s*(sqft|sq\s*ft|sq\.ft|square\s*feet)\b", q_lower)
            or "spacious" in q_lower
        ):
            core_filter_count += 1

        # 5. Locality indicators
        if any(
            loc in q_lower
            for loc in [
                "in ",
                "near ",
                "around ",
                "at ",
                "whitefield",
                "indiranagar",
                "koramangala",
                "hsr",
                "electronic city",
                "hebbal",
                "yelahanka",
                "bellandur",
            ]
        ):
            core_filter_count += 1

        # 6. POI categories
        known_pois = [
            "hospital",
            "clinic",
            "school",
            "college",
            "metro",
            "transit",
            "station",
            "park",
            "supermarket",
            "grocery",
            "mall",
            "gym",
            "bank",
            "pharmacy",
        ]
        for p in known_pois:
            if p in q_lower:
                poi_matches += 1

        # 7. Commute destination indicators
        if any(
            w in q_lower
            for w in [
                "commute to",
                "office in",
                "near tech park",
                "distance to",
                "travel to",
                "minutes to",
                "mins from",
                "drive to",
            ]
        ):
            has_commute = True

        # 8. Comparison indicators
        if any(
            w in q_lower
            for w in ["better than", "compare with", "versus", "vs", "difference between"]
        ):
            is_comparison = True

        # Compute deterministic complexity score
        complexity_score = 0
        if core_filter_count > 0:
            complexity_score += 1  # Core filters grouped together contribute 1 base point

        if poi_matches >= 2:
            complexity_score += 2  # Multi-POI reasoning

        if has_commute:
            complexity_score += 2  # Commute destination reasoning

        if is_comparison:
            complexity_score += 2  # Multi-entity comparative reasoning

        if len(query) > 100:
            complexity_score += 2  # Long multi-clause query reasoning

        is_complex = complexity_score >= settings.AI_ROUTING_COMPLEXITY_THRESHOLD

        return AIRequestProfile(
            operation="search_intent",
            query_length=len(query),
            core_filter_count=core_filter_count,
            poi_count=poi_matches,
            has_commute_target=has_commute,
            has_multiple_pois=(poi_matches >= 2),
            complexity_score=complexity_score,
            is_complex=is_complex,
        )

    @classmethod
    def profile_explanation_context(cls, context: dict[str, Any]) -> AIRequestProfile:
        """
        Analyze a property explanation context dictionary.
        """
        loc_intel = context.get("location_intelligence_3km", {})
        commute = context.get("commute")
        poi_count = len(loc_intel)
        has_commute = commute is not None

        complexity_score = 1  # Base property context
        if poi_count >= 2:
            complexity_score += 2
        if has_commute:
            complexity_score += 2

        is_complex = complexity_score >= settings.AI_ROUTING_COMPLEXITY_THRESHOLD

        return AIRequestProfile(
            operation="property_explanation",
            query_length=len(str(context)),
            core_filter_count=4,
            poi_count=poi_count,
            has_commute_target=has_commute,
            has_multiple_pois=(poi_count >= 2),
            complexity_score=complexity_score,
            is_complex=is_complex,
        )

    @classmethod
    def profile_comparison_context(cls, context: dict[str, Any]) -> AIRequestProfile:
        """
        Analyze a multi-property comparison context dictionary.
        2-property standard comparisons score < 3 (Ollama local).
        3-property or rich multi-dimensional comparisons score >= 3 (Gemini hosted).
        """
        properties = context.get("properties", {})
        prop_count = len(properties) if isinstance(properties, dict) else 2
        has_commute = False
        poi_count = 0

        if isinstance(properties, dict):
            for p in properties.values():
                if isinstance(p, dict):
                    if p.get("commute") is not None:
                        has_commute = True
                    poi_count += len(p.get("location_intelligence", {}))

        # Base complexity based on property count
        complexity_score = 2 if prop_count <= 2 else 3

        if has_commute:
            complexity_score += 2
        if poi_count >= 4:
            complexity_score += 2

        is_complex = complexity_score >= settings.AI_ROUTING_COMPLEXITY_THRESHOLD

        return AIRequestProfile(
            operation="property_comparison",
            query_length=len(str(context)),
            core_filter_count=prop_count * 3,
            poi_count=poi_count,
            has_commute_target=has_commute,
            has_multiple_pois=(poi_count >= 2),
            complexity_score=complexity_score,
            is_complex=is_complex,
        )

    @classmethod
    def profile_conversational_query(
        cls, user_message: str, current_state: dict[str, Any]
    ) -> AIRequestProfile:
        """
        Analyze a conversational search message within the context of the current search state.
        Simple single-field refinements (e.g., 'make it 3 BHK', 'reset') stay with local Ollama.
        Multi-constraint conversational updates or commute/POI additions route to Gemini.
        """
        base_profile = cls.profile_intent_query(user_message)
        complexity_score = base_profile.complexity_score

        # Check if user message involves comparison
        msg_lower = user_message.strip().lower()
        if "compare" in msg_lower:
            complexity_score += 2

        # If current state already has rich context and user is refining multiple dimensions
        if current_state.get("commute_destination") and base_profile.poi_count > 0:
            complexity_score += 1

        is_complex = complexity_score >= settings.AI_ROUTING_COMPLEXITY_THRESHOLD

        return AIRequestProfile(
            operation="conversational_search",
            query_length=len(user_message),
            core_filter_count=base_profile.core_filter_count,
            poi_count=base_profile.poi_count,
            has_commute_target=base_profile.has_commute_target
            or bool(current_state.get("commute_destination")),
            has_multiple_pois=base_profile.has_multiple_pois,
            complexity_score=complexity_score,
            is_complex=is_complex,
        )

    @classmethod
    def select_providers(
        cls,
        profile: AIRequestProfile,
        configured_mode: str | None = None,
    ) -> tuple[list[str], str]:
        """
        Determine the primary provider and bounded failover chain based on profile and settings.
        Returns: (attempt_order: list[str], routing_reason: str)
        """
        mode = (configured_mode or settings.AI_PROVIDER).lower()

        if mode == "mock":
            return ["mock"], "Static provider configuration: mock"
        elif mode == "ollama":
            return ["ollama"], "Static provider configuration: ollama (local)"
        elif mode == "gemini":
            return ["gemini"], "Static provider configuration: gemini (hosted)"
        elif mode == "auto":
            # Deterministic auto-routing heuristic
            if profile.is_complex:
                primary = "gemini" if settings.GEMINI_API_KEY else "ollama"
                secondary = "ollama" if primary == "gemini" else "gemini"
                reason = (
                    f"Auto-routed to {primary.upper()} (complex {profile.operation} with "
                    f"score {profile.complexity_score} >= threshold {settings.AI_ROUTING_COMPLEXITY_THRESHOLD}; "
                    f"fallback: {secondary.upper()})"
                )
                return [primary, secondary], reason
            else:
                primary = "ollama"
                secondary = "gemini"
                reason = (
                    f"Auto-routed to {primary.upper()} (standard {profile.operation} with "
                    f"score {profile.complexity_score} < threshold {settings.AI_ROUTING_COMPLEXITY_THRESHOLD}; "
                    f"fallback: {secondary.upper()})"
                )
                return [primary, secondary], reason
        else:
            from app.core.exceptions import AIProviderConfigurationException

            raise AIProviderConfigurationException(
                f"Unsupported AI provider mode: '{mode}'. Supported modes: ['ollama', 'gemini', 'mock', 'auto']"
            )
