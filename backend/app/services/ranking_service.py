from __future__ import annotations

import math
import time
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKeys, CacheService
from app.core.config import settings
from app.core.logging import logger
from app.models.property import Property
from app.repositories.property_repository import PropertyRepository
from app.schemas.geo import (
    BoundingBoxSearchParams,
    CategoryIntelligence,
    RadiusSearchParams,
)
from app.schemas.property import PropertyFilterParams, PropertyResponse
from app.schemas.ranking import (
    FactorScoreDetail,
    RankedPropertyItem,
    RankedSearchRequest,
    RankedSearchResponse,
    RankingConfigResponse,
)
from app.services.commute_service import CommuteService
from app.services.poi_service import POIService
from app.utils.geo import coords_from_point
from app.utils.ranking import (
    calculate_area_score,
    calculate_bedroom_score,
    calculate_commute_score,
    calculate_locality_score,
    calculate_location_score,
    calculate_price_score,
    generate_deterministic_explanations,
)


class RankingService:
    """
    Domain service for deterministic property ranking and explainable recommendations.
    Orchestrates:
    1. Database-side hard filtering and bounded candidate retrieval.
    2. Authoritative location intelligence and commute enrichment.
    3. Multi-factor normalized scoring with proportional weight redistribution.
    4. Deterministic tie-breaking (Score DESC -> Price ASC -> ID ASC).
    5. Factual template-based explanation generation.
    6. Sub-millisecond Redis response caching.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.property_repo = PropertyRepository(session)
        self.poi_service = POIService(session)
        self.commute_service = CommuteService(session)

    async def _retrieve_candidates(
        self, request: RankedSearchRequest
    ) -> tuple[list[Property], int]:
        """
        Execute database-level hard filtering in PostgreSQL/PostGIS.
        Enforces candidate limit (MAX_RANKING_CANDIDATES) to prevent unbounded retrieval.
        """
        candidate_cap = settings.MAX_RANKING_CANDIDATES

        # Case 1: Radius-constrained search
        if (
            request.center_lat is not None
            and request.center_lng is not None
            and request.radius_km is not None
        ):
            radius_params = RadiusSearchParams(
                latitude=request.center_lat,
                longitude=request.center_lng,
                radius_km=request.radius_km,
                min_price=request.min_price,
                max_price=request.max_price,
                bedrooms=request.bedrooms,
                bathrooms=request.bathrooms,
                property_type=request.property_type,
                status=request.status,
                limit=candidate_cap,
                offset=0,
            )
            items_with_dist, total = await self.property_repo.search_radius(radius_params)
            return [item[0] for item in items_with_dist], total

        # Case 2: Bounding box-constrained search
        if (
            request.min_lat is not None
            and request.max_lat is not None
            and request.min_lng is not None
            and request.max_lng is not None
        ):
            bbox_params = BoundingBoxSearchParams(
                min_lat=request.min_lat,
                max_lat=request.max_lat,
                min_lng=request.min_lng,
                max_lng=request.max_lng,
                min_price=request.min_price,
                max_price=request.max_price,
                bedrooms=request.bedrooms,
                bathrooms=request.bathrooms,
                property_type=request.property_type,
                status=request.status,
                limit=candidate_cap,
                offset=0,
            )
            return await self.property_repo.search_bbox(bbox_params)

        # Case 3: Standard attribute & locality search
        filter_params = PropertyFilterParams(
            city=request.city,
            locality=request.locality,
            property_type=request.property_type,
            min_price=request.min_price,
            max_price=request.max_price,
            bedrooms=request.bedrooms,
            bathrooms=request.bathrooms,
            status=request.status,
            page=1,
            page_size=candidate_cap,
            sort_by="newest",
        )
        items, total, _ = await self.property_repo.list(filter_params)
        return items, total

    async def rank_properties(self, request: RankedSearchRequest) -> RankedSearchResponse:
        """
        Execute deterministic ranking pipeline on eligible candidate properties.
        Caches results in Redis with CACHE_RANKING_TTL_SECONDS.
        """
        cache_key = CacheKeys.ranking(request.model_dump())
        cached_resp: RankedSearchResponse | None = await CacheService.get_json(
            cache_key, target_cls=RankedSearchResponse
        )
        if cached_resp is not None:
            logger.debug("Ranking cache HIT for key '%s'", cache_key)
            return cached_resp

        logger.debug("Ranking cache MISS for key '%s'", cache_key)
        start_time = time.perf_counter()

        # Step 1: Candidate retrieval
        candidates, total_candidates = await self._retrieve_candidates(request)
        if not candidates:
            empty_resp = RankedSearchResponse(
                total_candidates=0,
                ranking_config=RankingConfigResponse(
                    algorithm_version=settings.RANKING_ALGORITHM_VERSION,
                    weights=request.weights,
                    candidate_pool_size=0,
                ),
                items=[],
                page=1,
                page_size=request.limit,
                total_pages=1,
            )
            await CacheService.set_json(
                cache_key, empty_resp, ttl=settings.CACHE_RANKING_TTL_SECONDS
            )
            return empty_resp

        # Step 2: Pool extrema calculation
        prices = [float(p.price) for p in candidates]
        areas = [float(p.area_sqft) for p in candidates]
        pool_min_price, pool_max_price = min(prices), max(prices)
        pool_min_area, pool_max_area = min(areas), max(areas)

        raw_weights = request.weights.normalize()

        evaluated_items: list[RankedPropertyItem] = []

        # Step 3: Enrich & score each candidate
        for prop in candidates:
            prop_lat, prop_lng = coords_from_point(prop.location)

            # Location intelligence enrichment
            location_intel: dict[Any, CategoryIntelligence] | None = None
            if raw_weights["location"] > 0.0:
                try:
                    intel_resp = await self.poi_service.get_location_intelligence(prop.id)
                    location_intel = intel_resp.categories
                except Exception as e:
                    logger.warning("Failed to fetch location intel for property %d: %s", prop.id, e)

            # Commute intelligence enrichment
            commute_duration_mins: float | None = None
            if raw_weights["commute"] > 0.0 and request.destination is not None:
                try:
                    route, _ = await self.commute_service.calculate_route(
                        origin_lat=prop_lat,
                        origin_lng=prop_lng,
                        dest_lat=request.destination.latitude,
                        dest_lng=request.destination.longitude,
                        mode=request.travel_mode,
                    )
                    commute_duration_mins = route.duration_minutes
                except Exception as e:
                    logger.warning("Failed to compute commute for property %d: %s", prop.id, e)

            # Calculate individual factor scores
            p_score, p_desc = calculate_price_score(
                price=float(prop.price),
                min_price=request.min_price,
                max_price=request.max_price,
                target_price=request.target_price,
                pool_min_price=pool_min_price,
                pool_max_price=pool_max_price,
            )
            b_score, b_desc = calculate_bedroom_score(
                bedrooms=prop.bedrooms,
                preferred_bedrooms=request.preferred_bedrooms or request.bedrooms,
            )
            a_score, a_desc = calculate_area_score(
                area_sqft=float(prop.area_sqft),
                min_area_sqft=request.min_area_sqft,
                pool_min_area=pool_min_area,
                pool_max_area=pool_max_area,
            )
            loc_score, loc_desc = calculate_locality_score(
                property_locality=prop.locality,
                preferred_locality=request.preferred_locality or request.locality,
            )
            poi_score, poi_avail, poi_desc = calculate_location_score(
                categories_intel=location_intel,
                preferred_categories=request.preferred_poi_categories,
            )
            comm_score, comm_avail, comm_desc = calculate_commute_score(
                duration_minutes=commute_duration_mins,
                destination_name=request.destination.name if request.destination else None,
            )

            # Missing Data Weight Redistribution Policy:
            # If commute or location intelligence is unavailable, redistribute its weight
            # proportionally among available active factors so total effective weight = 1.0.
            available_factors: dict[str, tuple[float, bool, str]] = {
                "price": (p_score, True, p_desc),
                "bedrooms": (b_score, True, b_desc),
                "area": (a_score, True, a_desc),
                "locality": (loc_score, True, loc_desc),
                "location": (poi_score, poi_avail, poi_desc),
                "commute": (comm_score, comm_avail, comm_desc),
            }

            active_weight_sum = sum(
                raw_weights[k] for k, (_, avail, _) in available_factors.items() if avail
            )
            if active_weight_sum <= 0:
                active_weight_sum = 1.0

            breakdown: dict[str, FactorScoreDetail] = {}
            final_weighted_sum = 0.0

            for factor_key, (f_score, is_avail, f_desc) in available_factors.items():
                if is_avail:
                    effective_weight = raw_weights[factor_key] / active_weight_sum
                    contribution = round(f_score * effective_weight * 100.0, 2)
                    final_weighted_sum += f_score * effective_weight
                else:
                    effective_weight = 0.0
                    contribution = 0.0

                raw_val = None
                if factor_key == "commute" and commute_duration_mins is not None:
                    raw_val = commute_duration_mins
                elif factor_key == "price":
                    raw_val = float(prop.price)
                elif factor_key == "area":
                    raw_val = float(prop.area_sqft)

                breakdown[factor_key] = FactorScoreDetail(
                    score=f_score,
                    weight=round(effective_weight, 4),
                    weighted_contribution=contribution,
                    available=is_avail,
                    description=f_desc,
                    raw_value=raw_val,
                )

            final_score = round(min(100.0, max(0.0, final_weighted_sum * 100.0)), 1)
            explanations = generate_deterministic_explanations(breakdown, prop)

            evaluated_items.append(
                RankedPropertyItem(
                    rank=1,  # Placeholder, assigned after sorting
                    property=PropertyResponse.model_validate(prop),
                    final_score=final_score,
                    score_breakdown=breakdown,
                    commute_duration_minutes=commute_duration_mins,
                    explanations=explanations,
                )
            )

        # Step 4: Deterministic Tie-Breaking
        # Priority 1: final_score DESC
        # Priority 2: price ASC
        # Priority 3: id ASC
        evaluated_items.sort(
            key=lambda item: (
                -item.final_score,
                float(item.property.price),
                item.property.id,
            )
        )

        # Step 5: Assign Ordinal Rank Numbers
        for idx, item in enumerate(evaluated_items):
            item.rank = idx + 1

        # Step 6: Pagination
        total_items = len(evaluated_items)
        page_num = (request.offset // request.limit) + 1
        total_pages = math.ceil(total_items / request.limit) if total_items > 0 else 1
        paginated_items = evaluated_items[request.offset : request.offset + request.limit]

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        logger.info(
            "Deterministic ranking completed | candidates=%d returned=%d elapsed_ms=%.2f",
            len(candidates),
            len(paginated_items),
            elapsed_ms,
        )

        response = RankedSearchResponse(
            total_candidates=total_candidates,
            ranking_config=RankingConfigResponse(
                algorithm_version=settings.RANKING_ALGORITHM_VERSION,
                weights=request.weights,
                candidate_pool_size=len(candidates),
            ),
            items=paginated_items,
            page=page_num,
            page_size=request.limit,
            total_pages=total_pages,
        )

        # Cache in Redis with configured ranking TTL
        await CacheService.set_json(
            cache_key,
            response,
            ttl=settings.CACHE_RANKING_TTL_SECONDS,
        )

        return response
