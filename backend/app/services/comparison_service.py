from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheKeys, CacheService
from app.core.config import settings
from app.core.exceptions import EntityNotFoundException
from app.core.logging import logger
from app.models.property import Property
from app.repositories.property_repository import PropertyRepository
from app.schemas.comparison import (
    ComparisonDimensionSummary,
    ComparisonResult,
    PropertyComparisonFact,
    PropertyComparisonRequest,
    RankingContributionDelta,
)
from app.schemas.geo import CategoryIntelligence
from app.schemas.ranking import FactorScoreDetail
from app.services.commute_service import CommuteService
from app.services.poi_service import POIService
from app.services.routing.models import TravelMode
from app.utils.geo import coords_from_point
from app.utils.ranking import (
    calculate_area_score,
    calculate_bedroom_score,
    calculate_commute_score,
    calculate_locality_score,
    calculate_location_score,
    calculate_price_score,
)


def format_inr_amount(amount: float) -> str:
    """Format INR currency amount into readable Lakhs / Crores string."""
    if amount >= 10_000_000:
        cr = amount / 10_000_000
        return f"₹{cr:.2f} Cr".rstrip("0").rstrip(".") if cr != int(cr) else f"₹{int(cr)} Cr"
    elif amount >= 100_000:
        lakh = amount / 100_000
        return f"₹{lakh:.2f} L" if lakh != int(lakh) else f"₹{int(lakh)} L"
    else:
        return f"₹{amount:,.0f}"


class ComparisonService:
    """
    Deterministic domain service for multi-property comparison (2–3 properties).
    All calculations (price differences, ₹/sqft, commute deltas, POI distances,
    ranking match scores, and factor contribution deltas) are computed strictly in Python.
    No LLM calls exist in this service.
    """

    LABELS = ["Property A", "Property B", "Property C"]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.property_repo = PropertyRepository(session)
        self.poi_service = POIService(session)
        self.commute_service = CommuteService(session)

    async def compare_properties(self, request: PropertyComparisonRequest) -> ComparisonResult:
        """
        Execute deterministic property comparison across price, space, location,
        commute, and ranking dimensions.
        """
        cache_key = CacheKeys.comparison(request.model_dump())
        cached_resp: ComparisonResult | None = await CacheService.get_json(
            cache_key, target_cls=ComparisonResult
        )
        if cached_resp is not None:
            logger.debug("Comparison cache HIT for key '%s'", cache_key)
            return cached_resp

        logger.debug("Comparison cache MISS for key '%s'", cache_key)

        # Step 1: Fetch properties by ID
        properties_map: dict[int, Property] = {}
        for pid in request.property_ids:
            prop = await self.property_repo.get_by_id(pid)
            if not prop:
                raise EntityNotFoundException("Property", pid)
            properties_map[pid] = prop

        # Preserve request order
        ordered_props = [properties_map[pid] for pid in request.property_ids]

        # Step 2: Extract candidate extrema for normalized scoring
        prices = [float(p.price) for p in ordered_props]
        areas = [float(p.area_sqft) for p in ordered_props]
        pool_min_price, pool_max_price = min(prices), max(prices)
        pool_min_area, pool_max_area = min(areas), max(areas)

        raw_weights = request.weights.normalize()
        prop_facts: list[PropertyComparisonFact] = []

        # Step 3: Compute authoritative facts & ranking score for each property
        for idx, prop in enumerate(ordered_props):
            label = self.LABELS[idx]
            prop_lat, prop_lng = coords_from_point(prop.location)
            price_val = float(prop.price)
            area_val = float(prop.area_sqft) if prop.area_sqft else None
            price_per_sqft = round(price_val / area_val, 2) if (area_val and area_val > 0) else None

            # Location intelligence
            loc_intel_map: dict[str, float | None] = {}
            categories_intel: dict[Any, CategoryIntelligence] | None = None
            try:
                intel_resp = await self.poi_service.get_location_intelligence(
                    prop.id, radius_km=3.0
                )
                categories_intel = intel_resp.categories
                for cat_key, cat_info in intel_resp.categories.items():
                    key_str = cat_key.value if hasattr(cat_key, "value") else str(cat_key)
                    loc_intel_map[key_str] = cat_info.nearest_distance_km
            except Exception as e:
                logger.warning("Failed to fetch location intel for property %d: %s", prop.id, e)

            # Commute intelligence
            commute_duration_mins: float | None = None
            commute_distance_km: float | None = None
            commute_destination_name: str | None = None

            if request.destination_lat is not None and request.destination_lng is not None:
                try:
                    mode_val = (
                        TravelMode(request.travel_mode)
                        if isinstance(request.travel_mode, str)
                        else request.travel_mode
                    )
                    commute_res = await self.commute_service.get_property_commute(
                        property_id=prop.id,
                        dest_lat=request.destination_lat,
                        dest_lng=request.destination_lng,
                        dest_name=request.destination_name,
                        mode=mode_val,
                    )
                    commute_duration_mins = commute_res.duration_minutes
                    commute_distance_km = commute_res.distance_km
                    commute_destination_name = (
                        request.destination_name
                        or f"{request.destination_lat:.4f}, {request.destination_lng:.4f}"
                    )
                except Exception as e:
                    logger.warning("Failed to compute commute for property %d: %s", prop.id, e)

            # Factor scores
            p_score, p_desc = calculate_price_score(
                price=price_val,
                min_price=None,
                max_price=None,
                target_price=request.target_price,
                pool_min_price=pool_min_price,
                pool_max_price=pool_max_price,
            )
            b_score, b_desc = calculate_bedroom_score(
                bedrooms=prop.bedrooms,
                preferred_bedrooms=request.preferred_bedrooms or prop.bedrooms,
            )
            a_score, a_desc = calculate_area_score(
                area_sqft=area_val or 0.0,
                min_area_sqft=request.min_area_sqft,
                pool_min_area=pool_min_area,
                pool_max_area=pool_max_area,
            )
            loc_score, loc_desc = calculate_locality_score(
                property_locality=prop.locality,
                preferred_locality=request.preferred_locality,
            )
            poi_score, poi_avail, poi_desc = calculate_location_score(
                categories_intel=categories_intel,
                preferred_categories=request.preferred_poi_categories,
            )
            comm_score, comm_avail, comm_desc = calculate_commute_score(
                duration_minutes=commute_duration_mins,
                destination_name=commute_destination_name,
            )

            # Weight redistribution for missing factors
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

            score_breakdown: dict[str, FactorScoreDetail] = {}
            final_weighted_sum = 0.0

            for factor_key, (f_score, is_avail, f_desc) in available_factors.items():
                if is_avail:
                    effective_weight = raw_weights[factor_key] / active_weight_sum
                    contribution = round(f_score * effective_weight * 100.0, 2)
                    final_weighted_sum += contribution
                    score_breakdown[factor_key] = FactorScoreDetail(
                        score=round(f_score, 4),
                        weight=round(effective_weight, 4),
                        weighted_contribution=contribution,
                        available=True,
                        description=f_desc,
                    )
                else:
                    score_breakdown[factor_key] = FactorScoreDetail(
                        score=0.0,
                        weight=0.0,
                        weighted_contribution=0.0,
                        available=False,
                        description=f_desc,
                    )

            ranking_score = round(min(100.0, max(0.0, final_weighted_sum)), 2)

            image_urls = (
                [img.image_url for img in sorted(prop.images, key=lambda x: x.display_order)]
                if hasattr(prop, "images") and prop.images
                else []
            )

            fact = PropertyComparisonFact(
                id=prop.id,
                label=label,
                title=prop.title,
                price=price_val,
                price_formatted=format_inr_amount(price_val),
                price_per_sqft=price_per_sqft,
                bedrooms=prop.bedrooms,
                bathrooms=float(prop.bathrooms) if prop.bathrooms else None,
                area_sqft=area_val,
                property_type=prop.property_type,
                address=prop.address,
                locality=prop.locality,
                city=prop.city,
                latitude=prop_lat,
                longitude=prop_lng,
                image_urls=image_urls,
                location_intelligence=loc_intel_map,
                commute_duration_mins=commute_duration_mins,
                commute_distance_km=commute_distance_km,
                commute_destination=commute_destination_name,
                ranking_score=ranking_score,
                score_breakdown=score_breakdown,
            )
            prop_facts.append(fact)

        # Step 4: Compute dimension summaries & best by dimension
        dimensions: dict[str, ComparisonDimensionSummary] = {}
        best_by_dim: dict[str, str | None] = {}
        deterministic_summary: list[str] = []

        # 4a. Price Dimension
        cheapest_prop = min(prop_facts, key=lambda p: p.price)
        best_by_dim["price"] = cheapest_prop.label
        price_notes: list[str] = []

        for i in range(len(prop_facts)):
            for j in range(i + 1, len(prop_facts)):
                p1, p2 = prop_facts[i], prop_facts[j]
                diff = abs(p1.price - p2.price)
                if diff > 0:
                    cheaper, expensive = (p1, p2) if p1.price < p2.price else (p2, p1)
                    note = f"{cheaper.label} is {format_inr_amount(diff)} cheaper than {expensive.label}."
                    price_notes.append(note)
                    deterministic_summary.append(note)

        dimensions["price"] = ComparisonDimensionSummary(
            dimension="price",
            best_property_label=cheapest_prop.label,
            best_metric_label=f"Lowest price ({cheapest_prop.price_formatted})",
            metric_name="Price",
            details={
                "cheapest_label": cheapest_prop.label,
                "lowest_price": cheapest_prop.price,
                "lowest_price_formatted": cheapest_prop.price_formatted,
            },
            comparison_notes=price_notes,
        )

        # 4b. Space Dimension (Area)
        valid_area_props = [p for p in prop_facts if p.area_sqft is not None]
        if valid_area_props:
            largest_prop = max(valid_area_props, key=lambda p: p.area_sqft or 0.0)
            best_by_dim["space"] = largest_prop.label
            space_notes: list[str] = []

            for i in range(len(prop_facts)):
                for j in range(i + 1, len(prop_facts)):
                    p1, p2 = prop_facts[i], prop_facts[j]
                    if p1.area_sqft and p2.area_sqft:
                        area_diff = abs(p1.area_sqft - p2.area_sqft)
                        if area_diff > 0:
                            bigger, smaller = (p1, p2) if p1.area_sqft > p2.area_sqft else (p2, p1)
                            note = f"{bigger.label} provides {area_diff:,.0f} sq.ft. more living area than {smaller.label}."
                            space_notes.append(note)
                            deterministic_summary.append(note)

            dimensions["space"] = ComparisonDimensionSummary(
                dimension="space",
                best_property_label=largest_prop.label,
                best_metric_label=f"Largest area ({largest_prop.area_sqft:,.0f} sq.ft.)",
                metric_name="Living Area",
                details={
                    "largest_label": largest_prop.label,
                    "largest_area_sqft": largest_prop.area_sqft,
                },
                comparison_notes=space_notes,
            )
        else:
            best_by_dim["space"] = None

        # 4c. Commute Dimension
        valid_commute_props = [p for p in prop_facts if p.commute_duration_mins is not None]
        if len(valid_commute_props) == len(prop_facts):
            fastest_prop = min(valid_commute_props, key=lambda p: p.commute_duration_mins or 9999.0)
            best_by_dim["commute"] = fastest_prop.label
            commute_notes: list[str] = []

            for i in range(len(prop_facts)):
                for j in range(i + 1, len(prop_facts)):
                    p1, p2 = prop_facts[i], prop_facts[j]
                    if (
                        p1.commute_duration_mins is not None
                        and p2.commute_duration_mins is not None
                    ):
                        c_diff = round(abs(p1.commute_duration_mins - p2.commute_duration_mins), 1)
                        if c_diff > 0:
                            faster, slower = (
                                (p1, p2)
                                if p1.commute_duration_mins < p2.commute_duration_mins
                                else (p2, p1)
                            )
                            note = f"{faster.label}'s commute is {c_diff} minutes shorter than {slower.label}."
                            commute_notes.append(note)
                            deterministic_summary.append(note)

            dimensions["commute"] = ComparisonDimensionSummary(
                dimension="commute",
                best_property_label=fastest_prop.label,
                best_metric_label=f"Shortest commute ({fastest_prop.commute_duration_mins:.1f} mins)",
                metric_name="Commute Time",
                details={
                    "fastest_label": fastest_prop.label,
                    "duration_mins": fastest_prop.commute_duration_mins,
                    "destination": fastest_prop.commute_destination,
                },
                comparison_notes=commute_notes,
            )
        else:
            best_by_dim["commute"] = None
            if valid_commute_props:
                missing_labels = [p.label for p in prop_facts if p.commute_duration_mins is None]
                dimensions["commute"] = ComparisonDimensionSummary(
                    dimension="commute",
                    best_property_label=None,
                    best_metric_label=None,
                    metric_name="Commute Time",
                    details={},
                    comparison_notes=[
                        f"Commute comparison unavailable for {', '.join(missing_labels)} because no verified route was computed."
                    ],
                )
            else:
                dimensions["commute"] = ComparisonDimensionSummary(
                    dimension="commute",
                    best_property_label=None,
                    best_metric_label=None,
                    metric_name="Commute Time",
                    details={},
                    comparison_notes=[
                        "No commute destination specified for travel time comparison."
                    ],
                )

        # 4d. Location / POI Dimension
        poi_notes: list[str] = []
        for key_poi, poi_title in [
            ("hospital", "hospital"),
            ("school", "school"),
            ("transit", "transit access"),
        ]:
            valid_poi_props = [
                p for p in prop_facts if p.location_intelligence.get(key_poi) is not None
            ]
            if len(valid_poi_props) >= 2:
                closest_p = min(
                    valid_poi_props,
                    key=lambda p: p.location_intelligence.get(key_poi) or 999.0,
                )
                dist_closest = closest_p.location_intelligence[key_poi]
                for other in valid_poi_props:
                    if other.id != closest_p.id:
                        dist_other = other.location_intelligence[key_poi]
                        delta_dist = round(abs(dist_other - dist_closest), 2)
                        if delta_dist > 0:
                            poi_notes.append(
                                f"{closest_p.label} is {delta_dist} km closer to the nearest {poi_title} than {other.label}."
                            )

        if poi_notes:
            deterministic_summary.extend(poi_notes[:2])

        dimensions["location"] = ComparisonDimensionSummary(
            dimension="location",
            best_property_label=None,
            best_metric_label="Proximity to key amenities",
            metric_name="Location Intelligence",
            details={},
            comparison_notes=poi_notes,
        )

        # 4e. Ranking Dimension & Mathematical Factor Contribution Deltas
        # Order by score DESC, price ASC, id ASC
        sorted_by_rank = sorted(
            prop_facts,
            key=lambda p: (-(p.ranking_score or 0.0), p.price, p.id),
        )
        highest_match = sorted_by_rank[0]
        best_by_dim["ranking"] = highest_match.label

        ranking_deltas: list[RankingContributionDelta] = []
        for i in range(len(sorted_by_rank)):
            for j in range(i + 1, len(sorted_by_rank)):
                winner, loser = sorted_by_rank[i], sorted_by_rank[j]
                net_delta = round((winner.ranking_score or 0.0) - (loser.ranking_score or 0.0), 2)

                factor_deltas: dict[str, float] = {}
                for f_key in ["commute", "price", "bedrooms", "area", "location", "locality"]:
                    w_contrib = winner.score_breakdown.get(f_key)
                    l_contrib = loser.score_breakdown.get(f_key)
                    w_val = w_contrib.weighted_contribution if w_contrib else 0.0
                    l_val = l_contrib.weighted_contribution if l_contrib else 0.0
                    f_diff = round(w_val - l_val, 2)
                    if abs(f_diff) >= 0.01:
                        factor_deltas[f_key] = f_diff

                # Sort drivers by absolute impact
                sorted_drivers = sorted(
                    factor_deltas.items(), key=lambda x: abs(x[1]), reverse=True
                )
                positive_drivers = [f"{k} (+{v:.1f})" for k, v in sorted_drivers if v > 0]
                negative_drivers = [f"{k} ({v:.1f})" for k, v in sorted_drivers if v < 0]

                if positive_drivers:
                    if negative_drivers:
                        summary_str = (
                            f"{winner.label} ranks {net_delta:.1f} points higher than {loser.label} mainly because "
                            f"{', '.join(positive_drivers[:2])} advantages outweigh {', '.join(negative_drivers[:1])}."
                        )
                    else:
                        summary_str = (
                            f"{winner.label} ranks {net_delta:.1f} points higher than {loser.label} due to "
                            f"{', '.join(positive_drivers[:2])} fit."
                        )
                else:
                    summary_str = f"{winner.label} and {loser.label} have closely matched ranking scores ({winner.ranking_score:.1f}% vs {loser.ranking_score:.1f}%)."

                ranking_deltas.append(
                    RankingContributionDelta(
                        winner_label=winner.label,
                        loser_label=loser.label,
                        winner_score=winner.ranking_score or 0.0,
                        loser_score=loser.ranking_score or 0.0,
                        net_score_delta=net_delta,
                        factor_deltas=factor_deltas,
                        summary=summary_str,
                    )
                )

        dimensions["ranking"] = ComparisonDimensionSummary(
            dimension="ranking",
            best_property_label=highest_match.label,
            best_metric_label=f"Highest match score ({highest_match.ranking_score:.1f}%)",
            metric_name="Ranking Match",
            details={
                "highest_match_label": highest_match.label,
                "highest_match_score": highest_match.ranking_score,
            },
            comparison_notes=[rd.summary for rd in ranking_deltas],
        )

        result = ComparisonResult(
            properties=prop_facts,
            dimensions=dimensions,
            ranking_deltas=ranking_deltas,
            deterministic_summary=deterministic_summary,
            best_by_dimension=best_by_dim,
        )

        await CacheService.set_json(cache_key, result, ttl=settings.CACHE_RANKING_TTL_SECONDS)
        return result
