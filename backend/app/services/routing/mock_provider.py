from __future__ import annotations

import math

from app.core.exceptions import ValidationException
from app.services.routing.models import RouteGeometry, RouteResult, TravelMode


class MockRoutingProvider:
    """
    Deterministic mock routing engine for unit tests and local development.
    Computes realistic road network distances, travel durations, and multi-segment
    LineString geometries without requiring external network calls or API keys.
    """

    @property
    def provider_name(self) -> str:
        return "mock"

    @property
    def supported_modes(self) -> set[TravelMode]:
        return {TravelMode.DRIVING, TravelMode.WALKING, TravelMode.CYCLING}

    @staticmethod
    def _haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Compute great-circle distance in meters using the Haversine formula."""
        r = 6371000.0  # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2.0) ** 2
            + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
        )
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    def _generate_waypoints(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        num_segments: int = 5,
    ) -> list[list[float]]:
        """
        Generate realistic intermediate waypoints along the route path.
        Follows RFC 7946 GeoJSON format: [[longitude, latitude], ...].
        """
        coords: list[list[float]] = [[round(origin_lng, 6), round(origin_lat, 6)]]

        # Generate intermediate interpolated coordinates with realistic road offset
        dx = dest_lng - origin_lng
        dy = dest_lat - origin_lat

        for i in range(1, num_segments):
            fraction = i / float(num_segments)
            # Add small deterministic perpendicular offset for road realism
            perp_offset = 0.0008 * math.sin(fraction * math.pi)
            inter_lat = origin_lat + dy * fraction + perp_offset * (1 if i % 2 == 0 else -1)
            inter_lng = origin_lng + dx * fraction + perp_offset * (-1 if i % 2 == 0 else 1)
            coords.append([round(inter_lng, 6), round(inter_lat, 6)])

        coords.append([round(dest_lng, 6), round(dest_lat, 6)])
        return coords

    async def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: TravelMode = TravelMode.DRIVING,
    ) -> RouteResult:
        """Calculate mock route metrics and geometry."""
        if mode not in self.supported_modes:
            raise ValidationException(
                f"Travel mode '{mode.value}' is not supported by mock provider. Supported modes: {[m.value for m in self.supported_modes]}",
                details={"mode": mode.value, "provider": self.provider_name},
            )

        straight_dist_m = self._haversine_distance_meters(
            origin_lat, origin_lng, dest_lat, dest_lng
        )

        # Mode configurations: detour factor and average urban speed (m/s)
        # Driving: 1.30x detour, ~32 km/h (8.89 m/s)
        # Cycling: 1.20x detour, ~15 km/h (4.17 m/s)
        # Walking: 1.15x detour, ~4.8 km/h (1.33 m/s)
        mode_configs = {
            TravelMode.DRIVING: {
                "detour": 1.30,
                "speed_mps": 8.89,
                "summary": "Via Primary Urban Arterial Roads",
            },
            TravelMode.CYCLING: {
                "detour": 1.20,
                "speed_mps": 4.17,
                "summary": "Via Local & Cycle-friendly Routes",
            },
            TravelMode.WALKING: {
                "detour": 1.15,
                "speed_mps": 1.33,
                "summary": "Via Pedestrian Walkways & Footpaths",
            },
        }

        config = mode_configs[mode]
        route_dist_m = round(straight_dist_m * config["detour"], 1)
        duration_s = round(route_dist_m / config["speed_mps"], 1)

        coordinates = self._generate_waypoints(
            origin_lat, origin_lng, dest_lat, dest_lng, num_segments=5
        )

        return RouteResult(
            distance_meters=route_dist_m,
            duration_seconds=duration_s,
            distance_km=round(route_dist_m / 1000.0, 2),
            duration_minutes=round(duration_s / 60.0, 1),
            mode=mode,
            geometry=RouteGeometry(type="LineString", coordinates=coordinates),
            summary=config["summary"],
            provider=self.provider_name,
        )
