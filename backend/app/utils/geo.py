import math
from typing import Any

from geoalchemy2 import WKBElement, WKTElement
from geoalchemy2.shape import from_shape, to_shape
from shapely.geometry import Point


def calculate_haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points on the Earth (in km)."""
    r = 6371.0  # Earth's radius in kilometers
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


def point_from_coords(latitude: float, longitude: float) -> WKBElement:
    """
    Convert (latitude, longitude) floats to a PostGIS 4326 WKBElement.
    Note: PostGIS Point convention is Point(x, y) = Point(longitude, latitude).
    """
    return from_shape(Point(longitude, latitude), srid=4326)


def coords_from_point(location: Any) -> tuple[float, float]:
    """
    Extract (latitude, longitude) floats from a PostGIS Geometry object.
    Returns: (latitude, longitude).
    """
    if location is None:
        return 0.0, 0.0

    if isinstance(location, WKBElement | WKTElement):
        shape = to_shape(location)
        return float(shape.y), float(shape.x)

    if isinstance(location, Point):
        return float(location.y), float(location.x)

    if hasattr(location, "x") and hasattr(location, "y"):
        return float(location.y), float(location.x)

    return 0.0, 0.0
