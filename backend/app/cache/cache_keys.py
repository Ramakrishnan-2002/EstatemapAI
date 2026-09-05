from __future__ import annotations

import hashlib
from typing import Any

from app.cache.serialization import serialize_json
from app.core.config import settings


class CacheKeys:
    """
    Standardized, versioned, and deterministic Redis cache key generators.
    All keys use the 'estatemap:{domain}:{version}:{params}' namespace.
    """

    PREFIX = "estatemap"
    V1 = "v1"

    @staticmethod
    def normalize_coord(coord: float, precision: int | None = None) -> float:
        """
        Normalize geographic coordinate to fixed precision.
        Default 4 decimals corresponds to ~11 meters spatial resolution.
        """
        prec = precision if precision is not None else settings.CACHE_COORDINATE_PRECISION
        return round(coord, prec)

    @staticmethod
    def hash_payload(payload: Any) -> str:
        """
        Generate a deterministic SHA-256 hex digest for any dictionary or Pydantic object.
        """
        canonical_str = serialize_json(payload, sort_keys=True)
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()[:16]

    # ------------------------------------------------------------------
    # Commute & Road Routing Keys
    # ------------------------------------------------------------------
    @classmethod
    def route(
        cls,
        provider: str,
        mode: str,
        orig_lat: float,
        orig_lng: float,
        dest_lat: float,
        dest_lng: float,
    ) -> str:
        o_lat = cls.normalize_coord(orig_lat)
        o_lng = cls.normalize_coord(orig_lng)
        d_lat = cls.normalize_coord(dest_lat)
        d_lng = cls.normalize_coord(dest_lng)
        return f"{cls.PREFIX}:route:{cls.V1}:{provider.lower()}:{mode.lower()}:{o_lat},{o_lng}:{d_lat},{d_lng}"

    # ------------------------------------------------------------------
    # POI & Location Intelligence Keys
    # ------------------------------------------------------------------
    @classmethod
    def poi_intelligence(cls, property_id: int, radius_km: float = 3.0) -> str:
        r = round(radius_km, 2)
        return f"{cls.PREFIX}:poi:{cls.V1}:property:{property_id}:radius:{r}"

    # ------------------------------------------------------------------
    # Map & Spatial Viewport Keys
    # ------------------------------------------------------------------
    @classmethod
    def map_properties(
        cls,
        north: float,
        south: float,
        east: float,
        west: float,
        filters: dict[str, Any] | None = None,
    ) -> str:
        n = cls.normalize_coord(north)
        s = cls.normalize_coord(south)
        e = cls.normalize_coord(east)
        w = cls.normalize_coord(west)
        f_hash = cls.hash_payload(filters or {})
        return f"{cls.PREFIX}:map:{cls.V1}:properties:{n}:{s}:{e}:{w}:{f_hash}"

    @classmethod
    def map_pois(
        cls,
        north: float,
        south: float,
        east: float,
        west: float,
        category: str | None = None,
    ) -> str:
        n = cls.normalize_coord(north)
        s = cls.normalize_coord(south)
        e = cls.normalize_coord(east)
        w = cls.normalize_coord(west)
        cat = category.lower() if category else "all"
        return f"{cls.PREFIX}:map:{cls.V1}:pois:{n}:{s}:{e}:{w}:{cat}"

    # ------------------------------------------------------------------
    # Ranking & Recommendation Keys
    # ------------------------------------------------------------------
    @classmethod
    def ranking(cls, request_dict: dict[str, Any]) -> str:
        """
        Generate cache key for deterministic ranked search.
        Includes algorithm version, hard filters, soft criteria, and weights.
        """
        # Canonicalize coordinates in request if present
        norm_dict = dict(request_dict)
        norm_dict["algo_version"] = settings.RANKING_ALGORITHM_VERSION

        for lat_key in ("center_lat", "min_lat", "max_lat"):
            if norm_dict.get(lat_key) is not None:
                norm_dict[lat_key] = cls.normalize_coord(float(norm_dict[lat_key]))
        for lng_key in ("center_lng", "min_lng", "max_lng"):
            if norm_dict.get(lng_key) is not None:
                norm_dict[lng_key] = cls.normalize_coord(float(norm_dict[lng_key]))

        if "destination" in norm_dict and isinstance(norm_dict["destination"], dict):
            dest = dict(norm_dict["destination"])
            if "latitude" in dest:
                dest["latitude"] = cls.normalize_coord(float(dest["latitude"]))
            if "longitude" in dest:
                dest["longitude"] = cls.normalize_coord(float(dest["longitude"]))
            norm_dict["destination"] = dest

        digest = cls.hash_payload(norm_dict)
        return f"{cls.PREFIX}:ranking:{cls.V1}:{digest}"

    # ------------------------------------------------------------------
    # Comparison Keys
    # ------------------------------------------------------------------
    @classmethod
    def comparison(cls, request_dict: dict[str, Any]) -> str:
        """
        Generate cache key for deterministic multi-property comparison.
        Canonicalizes property IDs order and coordinates.
        """
        norm_dict = dict(request_dict)
        if "property_ids" in norm_dict and isinstance(norm_dict["property_ids"], list):
            norm_dict["property_ids"] = sorted(norm_dict["property_ids"])
        if norm_dict.get("destination_lat") is not None:
            norm_dict["destination_lat"] = cls.normalize_coord(float(norm_dict["destination_lat"]))
        if norm_dict.get("destination_lng") is not None:
            norm_dict["destination_lng"] = cls.normalize_coord(float(norm_dict["destination_lng"]))

        digest = cls.hash_payload(norm_dict)
        return f"{cls.PREFIX}:comparison:{cls.V1}:{digest}"

    # ------------------------------------------------------------------
    # Invalidation Pattern Generators
    # ------------------------------------------------------------------
    @classmethod
    def pattern_map(cls) -> str:
        return f"{cls.PREFIX}:map:{cls.V1}:*"

    @classmethod
    def pattern_ranking(cls) -> str:
        return f"{cls.PREFIX}:ranking:{cls.V1}:*"

    @classmethod
    def pattern_comparison(cls) -> str:
        return f"{cls.PREFIX}:comparison:{cls.V1}:*"

    @classmethod
    def pattern_poi(cls) -> str:
        return f"{cls.PREFIX}:poi:{cls.V1}:*"

    @classmethod
    def pattern_poi_property(cls, property_id: int) -> str:
        return f"{cls.PREFIX}:poi:{cls.V1}:property:{property_id}:*"

    @classmethod
    def pattern_route(cls) -> str:
        return f"{cls.PREFIX}:route:{cls.V1}:*"
