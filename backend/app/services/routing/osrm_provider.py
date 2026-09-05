from __future__ import annotations

import httpx

from app.core.config import settings
from app.core.exceptions import ExternalServiceException, ValidationException
from app.core.logging import logger
from app.services.routing.models import RouteGeometry, RouteResult, TravelMode


class OSRMProvider:
    """
    Open Source Routing Machine (OSRM) HTTP routing provider.
    Communicates with an OSRM backend via REST API for live road network calculations.
    """

    def __init__(
        self,
        base_url: str | None = None,
        timeout: float = 5.0,
    ) -> None:
        self.base_url = (base_url or settings.OSRM_BASE_URL).rstrip("/")
        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        return "osrm"

    @property
    def supported_modes(self) -> set[TravelMode]:
        return {TravelMode.DRIVING, TravelMode.WALKING, TravelMode.CYCLING}

    def _mode_to_profile(self, mode: TravelMode) -> str:
        mapping = {
            TravelMode.DRIVING: "driving",
            TravelMode.WALKING: "foot",
            TravelMode.CYCLING: "bike",
        }
        if mode not in mapping:
            raise ValidationException(
                f"Travel mode '{mode.value}' is not supported by OSRM.",
                details={"mode": mode.value, "provider": self.provider_name},
            )
        return mapping[mode]

    async def get_route(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float,
        mode: TravelMode = TravelMode.DRIVING,
    ) -> RouteResult:
        """Call OSRM Route service with GeoJSON geometry output."""
        profile = self._mode_to_profile(mode)
        # OSRM expects coordinates formatted as {lon},{lat};{lon},{lat}
        url = f"{self.base_url}/route/v1/{profile}/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
        params = {
            "overview": "full",
            "geometries": "geojson",
            "steps": "false",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)

            if response.status_code != 200:
                logger.warning(
                    "OSRM routing request failed with HTTP %d: %s",
                    response.status_code,
                    response.text,
                )
                raise ExternalServiceException(
                    "OSRM",
                    f"Routing service returned HTTP status {response.status_code}.",
                )

            data = response.json()
            if data.get("code") != "Ok" or not data.get("routes"):
                logger.warning("OSRM response error code: %s", data.get("code"))
                raise ExternalServiceException(
                    "OSRM",
                    f"No route found by routing service ({data.get('code')}).",
                )

            primary_route = data["routes"][0]
            distance_m = float(primary_route.get("distance", 0.0))
            duration_s = float(primary_route.get("duration", 0.0))
            geometry_data = primary_route.get("geometry", {})
            coordinates = geometry_data.get("coordinates", [])

            # Fallback if geometry is missing or degenerate
            if not coordinates or len(coordinates) < 2:
                coordinates = [
                    [round(origin_lng, 6), round(origin_lat, 6)],
                    [round(dest_lng, 6), round(dest_lat, 6)],
                ]

            return RouteResult(
                distance_meters=distance_m,
                duration_seconds=duration_s,
                distance_km=round(distance_m / 1000.0, 2),
                duration_minutes=round(duration_s / 60.0, 1),
                mode=mode,
                geometry=RouteGeometry(type="LineString", coordinates=coordinates),
                summary=primary_route.get("legs", [{}])[0].get("summary") or "OSRM Computed Route",
                provider=self.provider_name,
            )

        except httpx.TimeoutException as e:
            logger.warning("OSRM routing request timed out: %s", e)
            raise ExternalServiceException(
                "OSRM",
                "Routing service request timed out.",
            ) from e
        except httpx.RequestError as e:
            logger.warning("OSRM routing connection error: %s", e)
            raise ExternalServiceException(
                "OSRM",
                f"Could not connect to routing service: {e}",
            ) from e
