from __future__ import annotations

import math
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.logging import logger
from app.schemas.commute import CommuteDestination
from app.schemas.comparison import PropertyComparisonRequest
from app.schemas.conversational_search import (
    AllowedSearchField,
    AppliedPatchFeedback,
    AskMapResponse,
    ConversationAction,
    ConversationalSearchState,
    SearchStatePatch,
)
from app.schemas.ranking import (
    RankedPropertyItem,
    RankedSearchRequest,
    RankedSearchResponse,
    RankingWeights,
)
from app.services.comparison_service import ComparisonService, format_inr_amount
from app.services.ranking_service import RankingService
from app.utils.location_resolver import LocationResolver

RANKING_PRESETS: dict[str, RankingWeights] = {
    "balanced": RankingWeights(
        price=0.25, bedrooms=0.20, area=0.10, location=0.20, commute=0.25, locality=0.0
    ),
    "budget_first": RankingWeights(
        price=0.50, bedrooms=0.15, area=0.10, location=0.10, commute=0.15, locality=0.0
    ),
    "commute_first": RankingWeights(
        price=0.15, bedrooms=0.15, area=0.05, location=0.15, commute=0.50, locality=0.0
    ),
    "space_first": RankingWeights(
        price=0.20, bedrooms=0.30, area=0.35, location=0.05, commute=0.10, locality=0.0
    ),
    "amenity_focused": RankingWeights(
        price=0.15, bedrooms=0.15, area=0.10, location=0.45, commute=0.15, locality=0.0
    ),
}


class SearchOrchestrator:
    """
    Deterministic domain orchestrator for conversational property search.
    Applies validated state patches, resolves spatial coordinates, delegates to
    PostgreSQL/PostGIS hard filtering and deterministic ranking, executes dedicated
    actions (comparison, explanations), and builds GeoJSON responses.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.ranking_service = RankingService(session)
        self.comparison_service = ComparisonService(session)

    @classmethod
    def apply_patch(
        cls, current_state: ConversationalSearchState, patch: SearchStatePatch
    ) -> tuple[ConversationalSearchState, AppliedPatchFeedback, list[str], str | None]:
        """
        Deterministically apply a validated SearchStatePatch to a ConversationalSearchState.
        Returns:
            - new_state: Updated canonical search state.
            - feedback: Categorized delta feedback (added, modified, removed, preserved).
            - notes: Textual descriptions of state transitions.
            - unresolved_destination: Destination query string that could not be resolved, if any.
        """
        if patch.requested_action == ConversationAction.RESET_SEARCH:
            new_state = ConversationalSearchState()
            feedback = AppliedPatchFeedback(
                removed=["Reset all search criteria to default."],
            )
            return new_state, feedback, ["Reset all search filters."], None

        state_dict = current_state.model_dump()
        new_state = ConversationalSearchState(**state_dict)

        feedback = AppliedPatchFeedback()
        notes: list[str] = []
        unresolved_destination: str | None = None

        # --- 1. Handle Explicit CLEAR Operations ---
        for clear_field in patch.clear_fields:
            if clear_field in (
                AllowedSearchField.PRICE,
                AllowedSearchField.MAX_PRICE,
                AllowedSearchField.MIN_PRICE,
            ):
                if new_state.max_price is not None or new_state.min_price is not None:
                    new_state.max_price = None
                    new_state.min_price = None
                    feedback.removed.append("Removed price constraints")
                    notes.append("Price limit cleared")
            elif clear_field == AllowedSearchField.BEDROOMS:
                if new_state.bedrooms is not None:
                    new_state.bedrooms = None
                    feedback.removed.append("Removed bedroom filter")
                    notes.append("Bedroom constraint cleared")
            elif clear_field == AllowedSearchField.BATHROOMS:
                if new_state.bathrooms is not None:
                    new_state.bathrooms = None
                    feedback.removed.append("Removed bathroom filter")
            elif clear_field == AllowedSearchField.MIN_AREA_SQFT:
                if new_state.min_area_sqft is not None:
                    new_state.min_area_sqft = None
                    feedback.removed.append("Removed minimum area requirement")
            elif clear_field == AllowedSearchField.PROPERTY_TYPE:
                if new_state.property_type is not None:
                    new_state.property_type = None
                    feedback.removed.append("Removed property type constraint")
            elif clear_field in (AllowedSearchField.LOCALITY, AllowedSearchField.CITY):
                if new_state.locality is not None or new_state.city is not None:
                    new_state.locality = None
                    new_state.city = None
                    feedback.removed.append("Removed locality constraint")
                    notes.append("Locality cleared")
            elif clear_field == AllowedSearchField.POI_CATEGORIES:
                if new_state.preferred_poi_categories:
                    new_state.preferred_poi_categories = []
                    feedback.removed.append("Cleared POI preferences")
            elif clear_field in (
                AllowedSearchField.COMMUTE,
                AllowedSearchField.COMMUTE_DESTINATION,
                AllowedSearchField.MAX_COMMUTE_MINUTES,
            ):
                if (
                    new_state.commute_destination is not None
                    or new_state.destination_lat is not None
                ):
                    new_state.commute_destination = None
                    new_state.destination_lat = None
                    new_state.destination_lng = None
                    new_state.max_commute_minutes = None
                    feedback.removed.append("Removed commute destination")
                    notes.append("Commute destination cleared")
            elif clear_field == AllowedSearchField.RANKING:
                new_state.ranking_preset = "balanced"
                new_state.ranking_weights = RANKING_PRESETS["balanced"]
                feedback.removed.append("Reset ranking preferences to balanced")
            elif clear_field == AllowedSearchField.VIEWPORT:
                new_state.viewport_bbox = None
                feedback.removed.append("Removed map viewport boundary constraint")

        # --- 2. Handle SET / REPLACE Operations ---
        if patch.min_price is not None:
            if current_state.min_price is None:
                feedback.added.append(f"Min price {format_inr_amount(patch.min_price)}")
            elif current_state.min_price != patch.min_price:
                feedback.modified.append(
                    f"Min price changed to {format_inr_amount(patch.min_price)}"
                )
            new_state.min_price = patch.min_price

        if patch.max_price is not None:
            if current_state.max_price is None:
                feedback.added.append(f"Budget limit {format_inr_amount(patch.max_price)}")
            elif current_state.max_price != patch.max_price:
                feedback.modified.append(f"Budget updated to {format_inr_amount(patch.max_price)}")
            new_state.max_price = patch.max_price

        if patch.bedrooms is not None:
            if current_state.bedrooms is None:
                feedback.added.append(f"{patch.bedrooms} BHK requirement")
            elif current_state.bedrooms != patch.bedrooms:
                feedback.modified.append(f"Bedrooms changed to {patch.bedrooms} BHK")
            new_state.bedrooms = patch.bedrooms

        if patch.bathrooms is not None:
            if current_state.bathrooms is None:
                feedback.added.append(f"{patch.bathrooms}+ bathrooms")
            else:
                feedback.modified.append(f"Bathrooms updated to {patch.bathrooms}+")
            new_state.bathrooms = patch.bathrooms

        if patch.min_area_sqft is not None:
            if current_state.min_area_sqft is None:
                feedback.added.append(f"Min area {patch.min_area_sqft:,.0f} sqft")
            else:
                feedback.modified.append(f"Min area updated to {patch.min_area_sqft:,.0f} sqft")
            new_state.min_area_sqft = patch.min_area_sqft

        if patch.property_type is not None:
            if current_state.property_type is None:
                feedback.added.append(f"Property type: {patch.property_type}")
            else:
                feedback.modified.append(f"Type changed to {patch.property_type}")
            new_state.property_type = patch.property_type

        if patch.city is not None:
            new_state.city = patch.city

        if patch.locality is not None:
            resolved_loc = LocationResolver.resolve_locality(patch.locality)
            target_locality_name = resolved_loc.name if resolved_loc else patch.locality
            if current_state.locality is None:
                feedback.added.append(f"Locality: {target_locality_name}")
            elif current_state.locality.lower() != target_locality_name.lower():
                feedback.modified.append(f"Locality changed to {target_locality_name}")
            new_state.locality = target_locality_name

        if patch.commute_destination is not None:
            dest_res = LocationResolver.resolve_destination(patch.commute_destination)
            if dest_res is not None:
                new_state.commute_destination = dest_res.name
                new_state.destination_lat = dest_res.latitude
                new_state.destination_lng = dest_res.longitude
                if current_state.commute_destination != dest_res.name:
                    if current_state.commute_destination is None:
                        feedback.added.append(f"Commute to {dest_res.name}")
                    else:
                        feedback.modified.append(f"Commute destination changed to {dest_res.name}")
            else:
                unresolved_destination = patch.commute_destination
                # Preserve existing destination state to avoid contaminating canonical search state
                new_state.commute_destination = current_state.commute_destination
                new_state.destination_lat = current_state.destination_lat
                new_state.destination_lng = current_state.destination_lng
                logger.info("Unresolved commute destination: '%s'", patch.commute_destination)

        if patch.travel_mode is not None:
            if current_state.travel_mode != patch.travel_mode:
                feedback.modified.append(f"Travel mode: {patch.travel_mode.value}")
            new_state.travel_mode = patch.travel_mode

        if patch.max_commute_minutes is not None:
            if current_state.max_commute_minutes is None:
                feedback.added.append(f"Max commute {patch.max_commute_minutes:.0f} mins")
            else:
                feedback.modified.append(
                    f"Max commute changed to {patch.max_commute_minutes:.0f} mins"
                )
            new_state.max_commute_minutes = patch.max_commute_minutes

        if patch.ranking_preset is not None:
            clean_preset = patch.ranking_preset.lower().strip()
            if clean_preset in RANKING_PRESETS:
                new_state.ranking_preset = clean_preset
                new_state.ranking_weights = RANKING_PRESETS[clean_preset]
                feedback.modified.append(f"Prioritizing {clean_preset.replace('_', ' ')}")

        # --- 3. Handle APPEND / REMOVE Operations ---
        current_pois = list(new_state.preferred_poi_categories)

        for poi in patch.add_poi_categories:
            poi_val = poi.value if hasattr(poi, "value") else str(poi)
            existing_vals = [p.value if hasattr(p, "value") else str(p) for p in current_pois]
            if poi not in current_pois and poi_val not in existing_vals:
                current_pois.append(poi)
                feedback.added.append(f"Near {poi_val.replace('_', ' ')}")

        for poi in patch.remove_poi_categories:
            poi_val = poi.value if hasattr(poi, "value") else str(poi)
            current_pois = [
                p for p in current_pois if (p.value if hasattr(p, "value") else str(p)) != poi_val
            ]
            feedback.removed.append(f"Removed {poi_val.replace('_', ' ')} preference")

        new_state.preferred_poi_categories = current_pois

        # --- 4. Populate Preserved Filters ---
        if (
            current_state.bedrooms is not None
            and patch.bedrooms is None
            and AllowedSearchField.BEDROOMS not in patch.clear_fields
        ):
            feedback.preserved.append(f"{current_state.bedrooms} BHK")
        if (
            current_state.max_price is not None
            and patch.max_price is None
            and AllowedSearchField.MAX_PRICE not in patch.clear_fields
            and AllowedSearchField.PRICE not in patch.clear_fields
        ):
            feedback.preserved.append(f"Under {format_inr_amount(current_state.max_price)}")
        if (
            current_state.locality is not None
            and patch.locality is None
            and AllowedSearchField.LOCALITY not in patch.clear_fields
        ):
            feedback.preserved.append(f"In {current_state.locality}")
        if (
            current_state.commute_destination is not None
            and patch.commute_destination is None
            and AllowedSearchField.COMMUTE not in patch.clear_fields
            and AllowedSearchField.COMMUTE_DESTINATION not in patch.clear_fields
        ):
            feedback.preserved.append(f"Commute to {current_state.commute_destination}")

        return new_state, feedback, notes, unresolved_destination

    def _build_geojson(
        self, items: list[RankedPropertyItem], destination: CommuteDestination | None = None
    ) -> dict[str, Any]:
        """Construct RFC 7946 GeoJSON FeatureCollection for map rendering."""
        features: list[dict[str, Any]] = []

        for item in items:
            prop = item.property
            lat = prop.latitude
            lng = prop.longitude
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lng, lat],
                    },
                    "properties": {
                        "id": prop.id,
                        "title": prop.title,
                        "price": prop.price,
                        "price_formatted": format_inr_amount(prop.price),
                        "bedrooms": prop.bedrooms,
                        "bathrooms": prop.bathrooms,
                        "area_sqft": prop.area_sqft,
                        "locality": prop.locality,
                        "city": prop.city,
                        "rank": item.rank,
                        "final_score": item.final_score,
                        "primary_image_url": prop.images[0].image_url if prop.images else None,
                    },
                }
            )

        if destination is not None:
            features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [destination.longitude, destination.latitude],
                    },
                    "properties": {
                        "type": "destination",
                        "name": destination.name or "Destination",
                    },
                }
            )

        return {
            "type": "FeatureCollection",
            "features": features,
        }

    async def execute(
        self,
        current_state: ConversationalSearchState,
        patch: SearchStatePatch,
        user_message: str,
        session_id: str | None = None,
        provider: str = "deterministic",
        model: str = "orchestrator",
        latency_ms: float = 0.0,
        fallback_used: bool = False,
        routing_reason: str | None = None,
    ) -> AskMapResponse:
        """
        Execute deterministic search orchestration based on the resolved state patch.
        """
        start_time = time.perf_counter()

        new_state, feedback, notes, unresolved_dest = self.apply_patch(current_state, patch)

        if unresolved_dest:
            total_time_ms = (time.perf_counter() - start_time) * 1000 + latency_ms
            # Retain current_state intact so unresolved queries do not pollute caller canonical state
            return AskMapResponse(
                session_id=session_id,
                message=f"I couldn't identify the exact location of '{unresolved_dest}' in Bengaluru. Could you specify a nearby tech park or major landmark (e.g., Manyata Tech Park, EcoSpace, Whitefield)?",
                action=ConversationAction.REFINE,
                state=current_state,
                applied_patch=patch,
                feedback=feedback,
                needs_clarification=True,
                clarification_prompt=f"Could you clarify the location of '{unresolved_dest}'?",
                provider=provider,
                model=model,
                latency_ms=round(total_time_ms, 2),
                fallback_used=fallback_used,
                routing_reason=routing_reason,
            )

        # Handle dedicated actions
        if patch.requested_action == ConversationAction.COMPARE:
            target_ids: list[int] = []

            if patch.target_property_indices:
                ranked_req = self._build_ranked_request(new_state)
                ranked_res = await self.ranking_service.rank_properties(ranked_req)
                for idx in patch.target_property_indices:
                    if 1 <= idx <= len(ranked_res.items):
                        target_ids.append(ranked_res.items[idx - 1].property.id)
            elif new_state.selected_property_ids and len(new_state.selected_property_ids) >= 2:
                target_ids = list(new_state.selected_property_ids[:3])

            if len(target_ids) >= 2:
                dest = None
                if new_state.destination_lat and new_state.destination_lng:
                    dest = CommuteDestination(
                        latitude=new_state.destination_lat,
                        longitude=new_state.destination_lng,
                        name=new_state.commute_destination or "Workplace",
                    )

                comp_req = PropertyComparisonRequest(
                    property_ids=target_ids,
                    destination=dest,
                    travel_mode=new_state.travel_mode,
                    weights=new_state.ranking_weights,
                )
                comp_result = await self.comparison_service.compare_properties(comp_req)
                total_time_ms = (time.perf_counter() - start_time) * 1000 + latency_ms

                return AskMapResponse(
                    session_id=session_id,
                    message=f"Here is a side-by-side comparison of {len(target_ids)} properties.",
                    action=ConversationAction.COMPARE,
                    state=new_state,
                    applied_patch=patch,
                    feedback=feedback,
                    comparison_result=comp_result,
                    provider=provider,
                    model=model,
                    latency_ms=round(total_time_ms, 2),
                    fallback_used=fallback_used,
                    routing_reason=routing_reason,
                )
            else:
                total_time_ms = (time.perf_counter() - start_time) * 1000 + latency_ms
                return AskMapResponse(
                    session_id=session_id,
                    message="Please specify which properties you'd like to compare (e.g., 'compare the top two' or select 2-3 properties).",
                    action=ConversationAction.COMPARE,
                    state=new_state,
                    applied_patch=patch,
                    feedback=feedback,
                    needs_clarification=True,
                    clarification_prompt="Which properties would you like to compare?",
                    provider=provider,
                    model=model,
                    latency_ms=round(total_time_ms, 2),
                    fallback_used=fallback_used,
                    routing_reason=routing_reason,
                )

        if patch.requested_action == ConversationAction.EXPLAIN:
            ranked_req = self._build_ranked_request(new_state)
            ranked_res = await self.ranking_service.rank_properties(ranked_req)

            target_idx = patch.target_property_indices[0] if patch.target_property_indices else 1
            if 1 <= target_idx <= len(ranked_res.items):
                target_item = ranked_res.items[target_idx - 1]
                total_time_ms = (time.perf_counter() - start_time) * 1000 + latency_ms
                return AskMapResponse(
                    session_id=session_id,
                    message=f"Property #{target_idx} ({target_item.property.title}) ranked #{target_idx} with a score of {target_item.final_score:.1f}/100.",
                    action=ConversationAction.EXPLAIN,
                    state=new_state,
                    applied_patch=patch,
                    feedback=feedback,
                    items=ranked_res.items,
                    total_matches=ranked_res.total_candidates,
                    explanation_bullets=target_item.explanations,
                    provider=provider,
                    model=model,
                    latency_ms=round(total_time_ms, 2),
                    fallback_used=fallback_used,
                    routing_reason=routing_reason,
                )

        # Standard Search / Refine / Clear / Reset Execution
        ranked_req = self._build_ranked_request(new_state)
        ranked_res = await self.ranking_service.rank_properties(ranked_req)

        # Dynamic AI Property Synthesis when 0 properties match a requested locality or city
        if ranked_res.total_candidates == 0:
            target_loc = new_state.locality or patch.locality
            target_city = new_state.city or patch.city

            if not target_loc and not target_city:
                resolved_loc = LocationResolver.resolve_locality(user_message)
                if resolved_loc:
                    target_loc = resolved_loc.name
                elif user_message and len(user_message.strip().split()) <= 4:
                    target_loc = user_message.strip()

            target = target_loc or target_city
            if target:
                from app.services.property_synthesizer import PropertySynthesizer

                synthesized = await PropertySynthesizer.synthesize_for_locality(
                    session=self.session,
                    locality=target_loc or target_city or target,
                    city=target_city or target_loc or target,
                    bedrooms=new_state.bedrooms,
                    property_type=new_state.property_type,
                    max_price=new_state.max_price,
                    count=5,
                )
                if synthesized:
                    if target_loc and not new_state.locality:
                        new_state.locality = target_loc
                    if target_city and not new_state.city:
                        new_state.city = target_city
                    feedback.added.append(f"AI Generated listings for {target}")
                    # Re-run search & ranking
                    ranked_req = self._build_ranked_request(new_state)
                    ranked_res = await self.ranking_service.rank_properties(ranked_req)

        items = ranked_res.items
        if new_state.max_commute_minutes is not None:
            filtered_items = []
            for itm in items:
                # Authoritative typed numeric commute duration field
                dur = itm.commute_duration_minutes
                if dur is None:
                    commute_factor = itm.score_breakdown.get("commute")
                    if (
                        commute_factor
                        and commute_factor.available
                        and commute_factor.raw_value is not None
                    ):
                        dur = commute_factor.raw_value

                # Hard constraint policy:
                # - duration <= max_commute_minutes -> keep
                # - duration > max_commute_minutes -> exclude
                # - duration missing / unavailable (None) -> exclude (fail closed)
                if dur is not None and dur <= new_state.max_commute_minutes:
                    filtered_items.append(itm)

            items = filtered_items

            # Re-index ordinal ranks
            for idx, itm in enumerate(items):
                itm.rank = idx + 1

            # Update ranked_search_response to remain perfectly consistent with filtered items
            total_pages = math.ceil(len(items) / ranked_res.page_size) if len(items) > 0 else 1
            ranked_res = RankedSearchResponse(
                total_candidates=len(items),
                ranking_config=ranked_res.ranking_config,
                items=items,
                page=1,
                page_size=ranked_res.page_size,
                total_pages=total_pages,
            )

        dest_obj = None
        if new_state.destination_lat and new_state.destination_lng:
            dest_obj = CommuteDestination(
                latitude=new_state.destination_lat,
                longitude=new_state.destination_lng,
                name=new_state.commute_destination or "Workplace",
            )

        if patch.requested_action == ConversationAction.COMPARE:
            compare_ids: list[int] = []
            if patch.target_property_indices:
                for idx in patch.target_property_indices:
                    if 1 <= idx <= len(items):
                        compare_ids.append(items[idx - 1].property.id)
            if not compare_ids and len(items) >= 2:
                compare_ids = [items[0].property.id, items[1].property.id]
            if compare_ids:
                new_state.selected_property_ids = compare_ids[:3]

        geojson = self._build_geojson(items, dest_obj)
        summary_msg = self._build_summary_message(new_state, patch, len(items), feedback)
        total_time_ms = (time.perf_counter() - start_time) * 1000 + latency_ms

        return AskMapResponse(
            session_id=session_id,
            message=summary_msg,
            action=patch.requested_action,
            state=new_state,
            applied_patch=patch,
            feedback=feedback,
            ranked_search_response=ranked_res,
            items=items,
            total_matches=len(items),
            map_geojson=geojson,
            provider=provider,
            model=model,
            latency_ms=round(total_time_ms, 2),
            fallback_used=fallback_used,
            routing_reason=routing_reason,
        )

    def _build_ranked_request(self, state: ConversationalSearchState) -> RankedSearchRequest:
        """Translate ConversationalSearchState into RankedSearchRequest."""
        dest = None
        if state.destination_lat is not None and state.destination_lng is not None:
            dest = CommuteDestination(
                latitude=state.destination_lat,
                longitude=state.destination_lng,
                name=state.commute_destination or "Workplace",
            )

        min_lat = state.viewport_bbox.min_lat if state.viewport_bbox else None
        max_lat = state.viewport_bbox.max_lat if state.viewport_bbox else None
        min_lng = state.viewport_bbox.min_lng if state.viewport_bbox else None
        max_lng = state.viewport_bbox.max_lng if state.viewport_bbox else None

        return RankedSearchRequest(
            min_price=state.min_price,
            max_price=state.max_price,
            bedrooms=state.bedrooms,
            bathrooms=state.bathrooms,
            property_type=state.property_type,
            city=state.city,
            locality=state.locality,
            status="active",
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            target_price=state.max_price,
            preferred_bedrooms=state.bedrooms,
            min_area_sqft=state.min_area_sqft,
            preferred_locality=state.locality,
            preferred_poi_categories=state.preferred_poi_categories
            if state.preferred_poi_categories
            else None,
            destination=dest,
            travel_mode=state.travel_mode,
            weights=state.ranking_weights,
            limit=settings.MAX_RANKING_CANDIDATES,
            offset=0,
        )

    def _build_summary_message(
        self,
        state: ConversationalSearchState,
        patch: SearchStatePatch,
        count: int,
        feedback: AppliedPatchFeedback,
    ) -> str:
        """Generate concise factual confirmation of applied filters and match count."""
        criteria_parts: list[str] = []
        if state.bedrooms:
            criteria_parts.append(f"{state.bedrooms} BHK")
        if state.property_type:
            criteria_parts.append(f"{state.property_type.capitalize()}")
        if state.locality:
            criteria_parts.append(f"in {state.locality}")
        elif state.city:
            criteria_parts.append(f"in {state.city}")
        if state.max_price:
            criteria_parts.append(f"under {format_inr_amount(state.max_price)}")
        if state.commute_destination:
            criteria_parts.append(f"near {state.commute_destination}")
        if state.preferred_poi_categories:
            pois = ", ".join(
                (p.value if hasattr(p, "value") else str(p)).replace("_", " ")
                for p in state.preferred_poi_categories
            )
            criteria_parts.append(f"near {pois}")

        crit_str = " ".join(criteria_parts) if criteria_parts else "available"

        if count == 0:
            return f"Found 0 properties matching {crit_str}. Try broadening your price or location criteria."
        elif count == 1:
            return f"Found 1 property matching {crit_str}."
        else:
            return f"Found {count} properties matching {crit_str}."
