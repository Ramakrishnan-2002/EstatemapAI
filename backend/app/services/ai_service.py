from __future__ import annotations

import asyncio
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.base import AIProvider
from app.ai.router import AIRouter
from app.ai.routing_policy import AIRoutingPolicy
from app.core.config import settings
from app.core.exceptions import (
    AIInvalidResponseException,
    AIModelNotAvailableException,
    AIOutputValidationException,
    AIProviderAuthFailedException,
    AIProviderRateLimitedException,
    AIProviderTimeoutException,
    AIProviderUnavailableException,
    AIQuotaExceededException,
    EntityNotFoundException,
)
from app.core.logging import logger
from app.repositories.property_repository import PropertyRepository
from app.schemas.ai import (
    AIExplanationRequest,
    AIExplanationResponse,
    AIHealthResponse,
    AIUsageMetadata,
    ParseSearchResponse,
    PropertySearchIntent,
    ProviderHealthDetail,
)
from app.schemas.comparison import (
    AIComparisonResponse,
    PropertyComparisonRequest,
)
from app.schemas.conversational_search import (
    AskMapRequest,
    AskMapResponse,
)
from app.services.commute_service import CommuteService
from app.services.comparison_service import ComparisonService
from app.services.poi_service import POIService
from app.services.search_orchestrator import SearchOrchestrator
from app.utils.price_parser import IndianPriceParser


class AIService:
    """
    Multi-Provider Orchestration Service for EstateMap AI.
    Guarantees:
    - Zero database queries performed by LLMs.
    - Zero SQL generation or arbitrary tool execution.
    - Strict Pydantic validation on all model responses.
    - True global request time budget bounded by AI_TOTAL_TIMEOUT_SECONDS.
    - Deterministic request-complexity auto-routing and bounded single-attempt failover.
    - High-quality deterministic fallback if all AI providers fail.
    - Sanitized allowlist context stripped of internal database primary keys and PII.
    """

    def __init__(
        self,
        db: AsyncSession,
        ai_provider: AIProvider | None = None,
    ) -> None:
        self.db = db
        self._provider = ai_provider

    def get_provider(self, name: str | None = None) -> AIProvider:
        if self._provider is not None:
            return self._provider
        return AIRouter.get_provider(name)

    @staticmethod
    def _classify_error(e: Exception) -> str:
        if isinstance(
            e,
            AIProviderTimeoutException
            | TimeoutError
            | asyncio.TimeoutError
            | AIProviderUnavailableException
            | AIProviderRateLimitedException,
        ):
            return "TRANSIENT"
        if isinstance(
            e,
            AIProviderAuthFailedException | AIModelNotAvailableException | AIQuotaExceededException,
        ):
            return "CONFIGURATION"
        if isinstance(e, AIInvalidResponseException | AIOutputValidationException):
            return "MODEL_OUTPUT"
        return "UNKNOWN"

    async def check_health(self) -> AIHealthResponse:
        """
        Check health and diagnostics across all configured providers.
        Accurately distinguishes configured, reachable, authenticated, and model_available states.
        """
        if not settings.AI_ENABLED:
            return AIHealthResponse(
                enabled=False,
                configured_provider="none",
                active_primary="none",
                provider="none",
                reachable=False,
                model="none",
                model_available=False,
                available_models=[],
                latency_ms=None,
                details={"message": "AI is globally disabled via AI_ENABLED=False"},
            )

        providers_health: dict[str, ProviderHealthDetail] = {}
        configured_providers = AIRouter.get_all_configured_providers()

        for name, prov in configured_providers.items():
            try:
                res = await prov.check_health()
                providers_health[name] = ProviderHealthDetail(
                    configured=res.get("configured", True),
                    reachable=res.get("reachable", False),
                    model=prov.model_name,
                    model_available=res.get("model_available", False),
                    available_models=res.get("available_models", []),
                    latency_ms=res.get("latency_ms"),
                    authenticated=res.get("authenticated"),
                    error=res.get("error"),
                )
            except Exception as e:
                logger.warning("Health probe failed for provider '%s': %s", name, e)
                providers_health[name] = ProviderHealthDetail(
                    configured=True,
                    reachable=False,
                    model=prov.model_name,
                    model_available=False,
                    available_models=[],
                    latency_ms=None,
                    authenticated=False if isinstance(e, AIProviderAuthFailedException) else None,
                    error=str(e),
                )

        primary_name = (
            settings.AI_PRIMARY_PROVIDER if settings.AI_PROVIDER == "auto" else settings.AI_PROVIDER
        )
        primary_detail = providers_health.get(
            primary_name,
            ProviderHealthDetail(
                configured=False,
                reachable=False,
                model="unknown",
                model_available=False,
            ),
        )

        return AIHealthResponse(
            enabled=True,
            configured_provider=settings.AI_PROVIDER,
            active_primary=primary_name,
            provider=primary_name,
            reachable=primary_detail.reachable,
            model=primary_detail.model,
            model_available=primary_detail.model_available,
            available_models=primary_detail.available_models,
            latency_ms=primary_detail.latency_ms,
            providers=providers_health,
        )

    async def parse_search_intent(self, user_query: str) -> ParseSearchResponse:
        """
        Extract structured search filters with deterministic multi-provider failover
        and true global request deadline budgeting.
        """
        profile = AIRoutingPolicy.profile_intent_query(user_query)
        attempt_order, routing_reason = AIRoutingPolicy.select_providers(profile)

        start_time = time.monotonic()
        deadline = start_time + settings.AI_TOTAL_TIMEOUT_SECONDS
        last_error: Exception | None = None
        executed_providers: list[str] = []

        for i, prov_name in enumerate(attempt_order):
            if prov_name in executed_providers:
                continue  # Loop prevention: each provider attempted at most once
            executed_providers.append(prov_name)

            remaining_budget = deadline - time.monotonic()
            if remaining_budget <= 0:
                logger.warning(
                    "Global AI timeout budget (%.1fs) exhausted before attempting provider '%s'",
                    settings.AI_TOTAL_TIMEOUT_SECONDS,
                    prov_name,
                )
                break

            prov = self.get_provider(prov_name)
            prov_timeout = getattr(prov, "_timeout_seconds", 20.0) or 20.0
            attempt_timeout = min(remaining_budget, prov_timeout)

            logger.info(
                "AI Intent parse attempt | provider=%s attempt_timeout=%.2fs remaining_budget=%.2fs",
                prov_name,
                attempt_timeout,
                remaining_budget,
            )

            try:
                intent, latency_ms = await asyncio.wait_for(
                    prov.parse_search_intent(user_query),
                    timeout=attempt_timeout,
                )

                # Deterministic price parsing enrichment if omitted
                if intent.max_price is None and intent.min_price is None:
                    parsed_price = IndianPriceParser.parse_inr(user_query)
                    if parsed_price is not None:
                        q_lower = user_query.lower()
                        if any(
                            w in q_lower
                            for w in ["under", "below", "max", "upto", "up to", "within", "<"]
                        ):
                            intent.max_price = parsed_price
                        elif any(w in q_lower for w in ["above", "min", "from", "at least", ">"]):
                            intent.min_price = parsed_price
                        else:
                            intent.max_price = parsed_price

                total_latency = round((time.monotonic() - start_time) * 1000, 2)
                usage: AIUsageMetadata | None = getattr(prov, "last_usage", None)
                fallback_used = i > 0

                logger.info(
                    "AI Intent parsed successfully | provider=%s model=%s latency=%sms fallback=%s reason=%s",
                    prov.provider_name,
                    prov.model_name,
                    total_latency,
                    fallback_used,
                    routing_reason,
                )

                return ParseSearchResponse(
                    provider=prov.provider_name,
                    model=prov.model_name,
                    intent=intent,
                    latency_ms=total_latency,
                    prompt_version=settings.AI_PROMPT_VERSION_INTENT,
                    fallback_used=fallback_used,
                    routing_reason=routing_reason,
                    usage=usage,
                )

            except (
                AIProviderUnavailableException,
                AIProviderTimeoutException,
                AIModelNotAvailableException,
                AIProviderRateLimitedException,
                AIProviderAuthFailedException,
                AIQuotaExceededException,
                AIInvalidResponseException,
                AIOutputValidationException,
                TimeoutError,
            ) as e:
                err_category = self._classify_error(e)
                logger.warning(
                    "Provider '%s' failed for intent parsing [category=%s]: %s (evaluating failover...)",
                    prov_name,
                    err_category,
                    e,
                )
                last_error = e
                continue
            except Exception as e:
                logger.error("Unexpected error in provider '%s': %s", prov_name, e)
                last_error = e
                continue

        # All providers failed or budget exhausted - deterministic rule fallback
        total_latency = round((time.monotonic() - start_time) * 1000, 2)
        logger.warning("All AI providers failed. Using deterministic price/intent fallback.")

        parsed_price = IndianPriceParser.parse_inr(user_query)
        fallback_intent = PropertySearchIntent(
            raw_query=user_query,
            max_price=parsed_price,
            confidence=0.5,
        )

        return ParseSearchResponse(
            provider="deterministic_fallback",
            model="rule_based_v1",
            intent=fallback_intent,
            latency_ms=total_latency,
            prompt_version="deterministic_v1",
            fallback_used=True,
            routing_reason=f"All providers ({', '.join(executed_providers)}) failed: {last_error}",
        )

    async def explain_property(
        self,
        property_id: int,
        request: AIExplanationRequest,
    ) -> AIExplanationResponse:
        """
        Generate a factual property explanation with allowlisted context and true global request deadline budgeting.
        """
        # 1. Fetch Authoritative Property Record
        prop_repo = PropertyRepository(self.db)
        property_obj = await prop_repo.get_by_id(property_id)
        if not property_obj:
            raise EntityNotFoundException("Property", property_id)

        # 2. Fetch Authoritative Location Intelligence
        poi_service = POIService(self.db)
        loc_intel = await poi_service.get_location_intelligence(
            property_id=property_id, radius_km=3.0
        )

        # 3. Fetch Commute if destination provided
        commute_data: dict[str, Any] | None = None
        if request.destination_lat is not None and request.destination_lng is not None:
            try:
                commute_service = CommuteService(self.db)
                commute_res = await commute_service.get_property_commute(
                    property_id=property_id,
                    dest_lat=request.destination_lat,
                    dest_lng=request.destination_lng,
                    dest_name=request.destination_name,
                    mode=request.travel_mode,
                )
                commute_data = {
                    "destination": request.destination_name
                    or f"{request.destination_lat:.4f}, {request.destination_lng:.4f}",
                    "distance_km": commute_res.distance_km,
                    "duration_minutes": commute_res.duration_minutes,
                    "travel_mode": request.travel_mode.value,
                }
            except Exception as e:
                logger.warning("Commute computation skipped for AI explanation: %s", e)

        # 4. Assemble Sanitized Allowlisted Context for Hosted Providers (No internal primary keys, no owner IDs, no PII)
        sanitized_provider_context = {
            "property": {
                "title": property_obj.title,
                "price_inr": float(property_obj.price),
                "price_in_lakhs": round(float(property_obj.price) / 100_000.0, 2),
                "bedrooms": property_obj.bedrooms,
                "bathrooms": float(property_obj.bathrooms) if property_obj.bathrooms else None,
                "area_sqft": property_obj.area_sqft,
                "locality": property_obj.locality,
                "city": property_obj.city,
                "property_type": property_obj.property_type,
            },
            "location_intelligence_3km": {
                (cat.value if hasattr(cat, "value") else str(cat)): {
                    "nearest_distance_km": cat_info.nearest_distance_km,
                    "count_nearby": cat_info.count_within_radius,
                }
                for cat, cat_info in loc_intel.categories.items()
                if cat_info.nearest_distance_km is not None
            },
            "commute": commute_data,
        }

        # Context for client response metadata
        factual_context = {
            "property": {
                "id": property_obj.id,
                **sanitized_provider_context["property"],
            },
            "location_intelligence_3km": sanitized_provider_context["location_intelligence_3km"],
            "commute": commute_data,
        }

        # 5. Determine Routing
        profile = AIRoutingPolicy.profile_explanation_context(sanitized_provider_context)
        attempt_order, routing_reason = AIRoutingPolicy.select_providers(profile)

        start_time = time.monotonic()
        deadline = start_time + settings.AI_TOTAL_TIMEOUT_SECONDS
        last_error: Exception | None = None
        executed_providers: list[str] = []

        for i, prov_name in enumerate(attempt_order):
            if prov_name in executed_providers:
                continue
            executed_providers.append(prov_name)

            remaining_budget = deadline - time.monotonic()
            if remaining_budget <= 0:
                logger.warning(
                    "Global AI timeout budget (%.1fs) exhausted before explanation attempt '%s'",
                    settings.AI_TOTAL_TIMEOUT_SECONDS,
                    prov_name,
                )
                break

            prov = self.get_provider(prov_name)
            prov_timeout = getattr(prov, "_timeout_seconds", 20.0) or 20.0
            attempt_timeout = min(remaining_budget, prov_timeout)

            logger.info(
                "AI Explain attempt | provider=%s attempt_timeout=%.2fs remaining_budget=%.2fs",
                prov_name,
                attempt_timeout,
                remaining_budget,
            )

            try:
                explanation_text, latency_ms = await asyncio.wait_for(
                    prov.explain_property(sanitized_provider_context),
                    timeout=attempt_timeout,
                )
                total_latency = round((time.monotonic() - start_time) * 1000, 2)
                usage: AIUsageMetadata | None = getattr(prov, "last_usage", None)
                fallback_used = i > 0

                return AIExplanationResponse(
                    property_id=property_id,
                    explanation=explanation_text,
                    provider=prov.provider_name,
                    model=prov.model_name,
                    latency_ms=total_latency,
                    fallback_used=fallback_used,
                    factual_context=factual_context,
                    prompt_version=settings.AI_PROMPT_VERSION_EXPLANATION,
                    routing_reason=routing_reason,
                    usage=usage,
                )
            except (
                AIProviderUnavailableException,
                AIProviderTimeoutException,
                AIModelNotAvailableException,
                AIProviderRateLimitedException,
                AIProviderAuthFailedException,
                AIQuotaExceededException,
                AIInvalidResponseException,
                AIOutputValidationException,
                TimeoutError,
            ) as e:
                err_category = self._classify_error(e)
                logger.warning(
                    "Provider '%s' failed for explanation [category=%s]: %s (trying fallback...)",
                    prov_name,
                    err_category,
                    e,
                )
                last_error = e
                continue
            except Exception as e:
                logger.error("Unexpected error in provider '%s': %s", prov_name, e)
                last_error = e
                continue

        # 6. Deterministic Rule-Based Fallback if all providers failed or budget exhausted
        total_latency = round((time.monotonic() - start_time) * 1000, 2)
        logger.warning(
            "All AI providers failed for explanation. Building deterministic rule-based summary."
        )

        parts = [
            f"{property_obj.bedrooms or ''} BHK {property_obj.property_type} in {property_obj.locality}, {property_obj.city} listed at ₹{property_obj.price:,.0f} ({property_obj.area_sqft:,.0f} sqft)."
        ]
        nearest_items = []
        for cat, cdata in sanitized_provider_context["location_intelligence_3km"].items():
            if cdata.get("nearest_distance_km") is not None:
                nearest_items.append(f"{cat.replace('_', ' ')} ({cdata['nearest_distance_km']} km)")
        if nearest_items:
            parts.append(f"Nearby essentials include {', '.join(nearest_items[:2])}.")
        if commute_data:
            parts.append(
                f"Estimated {commute_data['travel_mode']} commute to {commute_data['destination']} is {commute_data['duration_minutes']} mins ({commute_data['distance_km']} km)."
            )
        explanation_text = " ".join(parts).strip()

        return AIExplanationResponse(
            property_id=property_id,
            explanation=explanation_text,
            provider="deterministic_fallback",
            model="rule_based_v1",
            latency_ms=total_latency,
            fallback_used=True,
            factual_context=factual_context,
            prompt_version=settings.AI_PROMPT_VERSION_EXPLANATION,
            routing_reason=f"All providers ({', '.join(executed_providers)}) failed: {last_error}",
        )

    async def explain_comparison(
        self,
        request: PropertyComparisonRequest,
    ) -> AIComparisonResponse:
        """
        Generate a comparative narrative for 2–3 properties.
        Comparison calculations (differences, price/sqft, commute deltas, ranking deltas)
        are computed deterministically FIRST by ComparisonService.
        The LLM only receives a sanitized allowlist context without internal DB IDs or PII.
        """
        # 1. Deterministic Comparison
        comparison_service = ComparisonService(self.db)
        comp_result = await comparison_service.compare_properties(request)

        # 2. Build Sanitized Allowlist Context (No internal primary keys, no owner IDs, no PII)
        sanitized_context = {
            "properties": {
                prop.label: {
                    "locality": prop.locality,
                    "city": prop.city,
                    "property_type": prop.property_type,
                    "price_inr": prop.price,
                    "price_formatted": prop.price_formatted,
                    "price_per_sqft": prop.price_per_sqft,
                    "bedrooms": prop.bedrooms,
                    "bathrooms": prop.bathrooms,
                    "area_sqft": prop.area_sqft,
                    "location_intelligence": prop.location_intelligence,
                    "commute": {
                        "duration_minutes": prop.commute_duration_mins,
                        "distance_km": prop.commute_distance_km,
                        "destination": prop.commute_destination,
                    }
                    if prop.commute_duration_mins is not None
                    else None,
                    "ranking_score": prop.ranking_score,
                }
                for prop in comp_result.properties
            },
            "verified_statements": comp_result.deterministic_summary,
            "ranking_deltas": [
                {
                    "winner": delta.winner_label,
                    "loser": delta.loser_label,
                    "net_score_delta": delta.net_score_delta,
                    "summary": delta.summary,
                }
                for delta in comp_result.ranking_deltas
            ],
            "best_by_dimension": comp_result.best_by_dimension,
        }

        # 3. Determine Routing
        profile = AIRoutingPolicy.profile_comparison_context(sanitized_context)
        attempt_order, routing_reason = AIRoutingPolicy.select_providers(profile)

        start_time = time.monotonic()
        deadline = start_time + settings.AI_TOTAL_TIMEOUT_SECONDS
        last_error: Exception | None = None
        executed_providers: list[str] = []

        for i, prov_name in enumerate(attempt_order):
            if prov_name in executed_providers:
                continue
            executed_providers.append(prov_name)

            remaining_budget = deadline - time.monotonic()
            if remaining_budget <= 0:
                logger.warning(
                    "Global AI timeout budget (%.1fs) exhausted before comparison attempt '%s'",
                    settings.AI_TOTAL_TIMEOUT_SECONDS,
                    prov_name,
                )
                break

            prov = self.get_provider(prov_name)
            prov_timeout = getattr(prov, "_timeout_seconds", 20.0) or 20.0
            attempt_timeout = min(remaining_budget, prov_timeout)

            logger.info(
                "AI Comparison attempt | provider=%s attempt_timeout=%.2fs remaining_budget=%.2fs",
                prov_name,
                attempt_timeout,
                remaining_budget,
            )

            try:
                narrative_text, latency_ms = await asyncio.wait_for(
                    prov.explain_comparison(sanitized_context),
                    timeout=attempt_timeout,
                )
                total_latency = round((time.monotonic() - start_time) * 1000, 2)
                usage: AIUsageMetadata | None = getattr(prov, "last_usage", None)
                fallback_used = i > 0

                return AIComparisonResponse(
                    comparison=comp_result,
                    narrative=narrative_text,
                    provider=prov.provider_name,
                    model=prov.model_name,
                    latency_ms=total_latency,
                    fallback_used=fallback_used,
                    prompt_version="property_comparison_v1",
                    routing_reason=routing_reason,
                    usage=usage,
                )
            except (
                AIProviderUnavailableException,
                AIProviderTimeoutException,
                AIModelNotAvailableException,
                AIProviderRateLimitedException,
                AIProviderAuthFailedException,
                AIQuotaExceededException,
                AIInvalidResponseException,
                AIOutputValidationException,
                TimeoutError,
            ) as e:
                err_category = self._classify_error(e)
                logger.warning(
                    "Provider '%s' failed for comparison [category=%s]: %s (trying fallback...)",
                    prov_name,
                    err_category,
                    e,
                )
                last_error = e
                continue
            except Exception as e:
                logger.error(
                    "Unexpected error in provider '%s' during comparison: %s", prov_name, e
                )
                last_error = e
                continue

        # 4. Deterministic Fallback if all providers failed or budget exhausted
        total_latency = round((time.monotonic() - start_time) * 1000, 2)
        logger.warning(
            "All AI providers failed for comparison. Building deterministic rule-based summary."
        )

        fallback_parts = []
        if comp_result.deterministic_summary:
            fallback_parts.extend(comp_result.deterministic_summary)
        for delta in comp_result.ranking_deltas:
            fallback_parts.append(delta.summary)

        narrative_text = " ".join(fallback_parts).strip()
        if not narrative_text:
            narrative_text = (
                "Deterministic comparison metrics and trade-offs computed successfully."
            )

        return AIComparisonResponse(
            comparison=comp_result,
            narrative=narrative_text,
            provider="deterministic_fallback",
            model="rule_based_v1",
            latency_ms=total_latency,
            fallback_used=True,
            prompt_version="deterministic_v1",
            routing_reason=f"All providers ({', '.join(executed_providers)}) failed: {last_error}",
        )

    async def ask_map(self, request: AskMapRequest) -> AskMapResponse:
        """
        Conversational Search Orchestration endpoint.
        Extracts validated SearchStatePatch from user natural language query,
        applies it to the canonical search state, and executes deterministic PostGIS/ranking services.
        Guarantees:
        - Strict facts-first boundary: LLM extracts intent, backend decides and executes.
        - Privacy allowlisting: No internal IDs or PII sent to LLMs.
        - Global time budget bounded by AI_TOTAL_TIMEOUT_SECONDS.
        - High-quality deterministic fallback if all AI providers fail.
        """
        orchestrator = SearchOrchestrator(self.db)
        start_time = time.monotonic()

        # Build sanitized state dictionary for LLM context allowlist
        sanitized_state = {
            "min_price": request.current_state.min_price,
            "max_price": request.current_state.max_price,
            "bedrooms": request.current_state.bedrooms,
            "bathrooms": request.current_state.bathrooms,
            "min_area_sqft": request.current_state.min_area_sqft,
            "property_type": request.current_state.property_type,
            "city": request.current_state.city,
            "locality": request.current_state.locality,
            "preferred_poi_categories": [
                p.value if hasattr(p, "value") else str(p)
                for p in request.current_state.preferred_poi_categories
            ],
            "commute_destination": request.current_state.commute_destination,
            "travel_mode": request.current_state.travel_mode.value
            if hasattr(request.current_state.travel_mode, "value")
            else str(request.current_state.travel_mode),
            "max_commute_minutes": request.current_state.max_commute_minutes,
            "ranking_preset": request.current_state.ranking_preset,
        }

        profile = AIRoutingPolicy.profile_conversational_query(request.message, sanitized_state)
        attempt_order, routing_reason = AIRoutingPolicy.select_providers(profile)

        deadline = start_time + settings.AI_TOTAL_TIMEOUT_SECONDS
        last_error: Exception | None = None
        executed_providers: list[str] = []

        for i, prov_name in enumerate(attempt_order):
            if prov_name in executed_providers:
                continue
            executed_providers.append(prov_name)

            remaining_budget = deadline - time.monotonic()
            if remaining_budget <= 0:
                logger.warning(
                    "Global AI timeout budget (%.1fs) exhausted before attempting provider '%s'",
                    settings.AI_TOTAL_TIMEOUT_SECONDS,
                    prov_name,
                )
                break

            prov = self.get_provider(prov_name)
            prov_timeout = getattr(prov, "_timeout_seconds", 20.0) or 20.0
            attempt_timeout = min(remaining_budget, prov_timeout)

            logger.info(
                "AI Ask-the-Map attempt | provider=%s attempt_timeout=%.2fs remaining_budget=%.2fs",
                prov_name,
                attempt_timeout,
                remaining_budget,
            )

            try:
                patch, prov_latency = await asyncio.wait_for(
                    prov.parse_search_patch(sanitized_state, request.message),
                    timeout=attempt_timeout,
                )

                total_latency = round((time.monotonic() - start_time) * 1000, 2)
                fallback_used = i > 0

                logger.info(
                    "AI Ask-the-Map patch extracted successfully | provider=%s model=%s latency=%sms fallback=%s",
                    prov.provider_name,
                    prov.model_name,
                    total_latency,
                    fallback_used,
                )

                return await orchestrator.execute(
                    current_state=request.current_state,
                    patch=patch,
                    user_message=request.message,
                    session_id=request.session_id,
                    provider=prov.provider_name,
                    model=prov.model_name,
                    latency_ms=total_latency,
                    fallback_used=fallback_used,
                    routing_reason=routing_reason,
                )

            except (
                AIProviderUnavailableException,
                AIProviderTimeoutException,
                AIModelNotAvailableException,
                AIProviderRateLimitedException,
                AIProviderAuthFailedException,
                AIQuotaExceededException,
                AIInvalidResponseException,
                AIOutputValidationException,
                TimeoutError,
            ) as e:
                err_category = self._classify_error(e)
                logger.warning(
                    "Provider '%s' failed for Ask-the-Map [category=%s]: %s (trying fallback...)",
                    prov_name,
                    err_category,
                    e,
                )
                last_error = e
                continue
            except Exception as e:
                logger.error(
                    "Unexpected error in provider '%s' during Ask-the-Map: %s", prov_name, e
                )
                last_error = e
                continue

        # Deterministic Rule-based Fallback if all AI providers failed
        total_latency = round((time.monotonic() - start_time) * 1000, 2)
        logger.warning(
            "All AI providers failed for Ask-the-Map. Invoking deterministic mock/rule-based patch extractor."
        )

        from app.ai.mock_provider import MockAIProvider

        fallback_prov = MockAIProvider()
        fallback_patch, _ = await fallback_prov.parse_search_patch(sanitized_state, request.message)

        return await orchestrator.execute(
            current_state=request.current_state,
            patch=fallback_patch,
            user_message=request.message,
            session_id=request.session_id,
            provider="deterministic_fallback",
            model="heuristic_patch_v1",
            latency_ms=total_latency,
            fallback_used=True,
            routing_reason=f"All providers ({', '.join(executed_providers)}) failed: {last_error}",
        )
