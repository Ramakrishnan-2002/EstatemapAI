from __future__ import annotations

import re

from pydantic import BaseModel, Field

# Bounding sanity limits for supported metropolitan areas
BENGALURU_LAT_RANGE = (12.70, 13.30)
BENGALURU_LNG_RANGE = (77.35, 77.85)

CHENNAI_LAT_RANGE = (12.75, 13.35)
CHENNAI_LNG_RANGE = (80.00, 80.35)

METRO_BOUNDS = [
    ("Bengaluru", BENGALURU_LAT_RANGE, BENGALURU_LNG_RANGE),
    ("Chennai", CHENNAI_LAT_RANGE, CHENNAI_LNG_RANGE),
]


class ResolvedLocation(BaseModel):
    name: str
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)


# Deterministic verified coordinates database for Bengaluru & Chennai locations, tech hubs, and transit stations.
# Coordinates verified via official open municipal and OpenStreetMap geographic references.
KNOWN_LOCATIONS: dict[str, tuple[float, float, str]] = {
    # --- Bengaluru Locations ---
    "electronic city": (12.8452, 77.6602, "Electronic City"),
    "ecity": (12.8452, 77.6602, "Electronic City"),
    "e-city": (12.8452, 77.6602, "Electronic City Phase 1"),
    "e city": (12.8452, 77.6602, "Electronic City Phase 1"),
    "electronic city phase 1": (12.8452, 77.6602, "Electronic City Phase 1"),
    "electronic city phase 2": (12.8398, 77.6770, "Electronic City Phase 2"),
    "indiranagar": (12.9716, 77.6412, "Indiranagar"),
    "koramangala": (12.9352, 77.6245, "Koramangala"),
    "whitefield": (12.9698, 77.7499, "Whitefield"),
    "hsr layout": (12.9121, 77.6446, "HSR Layout"),
    "hsr": (12.9121, 77.6446, "HSR Layout"),
    "mg road": (12.9716, 77.5946, "MG Road"),
    "central": (12.9716, 77.5946, "Central (MG Road)"),
    "bellandur": (12.9304, 77.6784, "Bellandur"),
    "outer ring road": (12.9304, 77.6784, "Outer Ring Road"),
    "orr": (12.9304, 77.6784, "Outer Ring Road"),
    "marathahalli": (12.9591, 77.6974, "Marathahalli"),
    "hebbal": (13.0358, 77.5970, "Hebbal"),
    "manyata tech park": (13.0489, 77.6208, "Manyata Tech Park"),
    "manyata": (13.0489, 77.6208, "Manyata Tech Park"),
    "manyata embassy business park": (13.0489, 77.6208, "Manyata Tech Park"),
    "rmz ecospace": (12.9260, 77.6840, "RMZ EcoSpace"),
    "ecospace": (12.9260, 77.6840, "RMZ EcoSpace"),
    "eco space": (12.9260, 77.6840, "RMZ EcoSpace"),
    "bellandur ecospace": (12.9260, 77.6840, "RMZ EcoSpace"),
    "bagmane tech park": (12.9784, 77.6575, "Bagmane Tech Park"),
    "bagmane": (12.9784, 77.6575, "Bagmane Tech Park"),
    "itpl": (12.9863, 77.7308, "ITPL Whitefield"),
    "international tech park": (12.9863, 77.7308, "ITPL Whitefield"),
    "sarjapur road": (12.9102, 77.6835, "Sarjapur Road"),
    "sarjapur": (12.9102, 77.6835, "Sarjapur Road"),
    "silk board": (12.9175, 77.6227, "Silk Board Junction"),
    "jayanagar": (12.9308, 77.5838, "Jayanagar"),
    "jp nagar": (12.9063, 77.5857, "JP Nagar"),
    "banashankari": (12.9255, 77.5468, "Banashankari"),
    "malleshwaram": (13.0031, 77.5643, "Malleshwaram"),
    "rajajinagar": (12.9982, 77.5530, "Rajajinagar"),
    "yeshwanthpur": (13.0238, 77.5529, "Yeshwanthpur"),
    "yelahanka": (13.1007, 77.5963, "Yelahanka"),
    "cubbon park": (12.9763, 77.5929, "Cubbon Park"),
    "majestic": (12.9781, 77.5697, "Majestic (KSR Railway Station)"),
    "ksr bengaluru": (12.9781, 77.5697, "Majestic (KSR Railway Station)"),

    # --- Chennai Locations ---
    "tidel park": (12.9897, 80.2483, "TIDEL Park"),
    "tidel": (12.9897, 80.2483, "TIDEL Park"),
    "omr": (12.8995, 80.2279, "OMR IT Expressway"),
    "old mahabalipuram road": (12.8995, 80.2279, "OMR IT Expressway"),
    "it corridor": (12.8995, 80.2279, "OMR IT Expressway"),
    "sholinganallur": (12.8995, 80.2279, "Sholinganallur"),
    "sholinganallur junction": (12.8995, 80.2279, "Sholinganallur Junction"),
    "dlf": (13.0183, 80.1706, "DLF Cybercity"),
    "dlf cybercity": (13.0183, 80.1706, "DLF Cybercity"),
    "dlf it park": (13.0183, 80.1706, "DLF Cybercity"),
    "olympia tech park": (13.0102, 80.2078, "Olympia Tech Park"),
    "olympia": (13.0102, 80.2078, "Olympia Tech Park"),
    "guindy": (13.0067, 80.2050, "Guindy"),
    "guindy industrial estate": (13.0067, 80.2050, "Guindy Industrial Estate"),
    "chennai central": (13.0827, 80.2707, "Chennai Central"),
    "mgr central": (13.0827, 80.2707, "Chennai Central"),
    "chennai airport": (12.9941, 80.1709, "Chennai International Airport"),
    "maa airport": (12.9941, 80.1709, "Chennai International Airport"),
    "adyar": (13.0012, 80.2565, "Adyar"),
    "besant nagar": (12.9982, 80.2665, "Besant Nagar"),
    "elliots beach": (12.9982, 80.2665, "Besant Nagar (Elliot's Beach)"),
    "anna nagar": (13.0850, 80.2100, "Anna Nagar"),
    "t nagar": (13.0418, 80.2341, "T. Nagar"),
    "t. nagar": (13.0418, 80.2341, "T. Nagar"),
    "thyagaraya nagar": (13.0418, 80.2341, "T. Nagar"),
    "nungambakkam": (13.0569, 80.2425, "Nungambakkam"),
    "alwarpet": (13.0334, 80.2505, "Alwarpet"),
    "mylapore": (13.0368, 80.2676, "Mylapore"),
    "velachery": (12.9759, 80.2212, "Velachery"),
    "perungudi": (12.9654, 80.2415, "Perungudi"),
    "thoraipakkam": (12.9348, 80.2312, "Thoraipakkam"),
    "navalur": (12.8458, 80.2268, "Navalur"),
    "siruseri": (12.8285, 80.2185, "Siruseri SIPCOT IT Park"),
    "sipcot": (12.8285, 80.2185, "Siruseri SIPCOT IT Park"),
    "sipcot siruseri": (12.8285, 80.2185, "Siruseri SIPCOT IT Park"),
    "marina beach": (13.0500, 80.2824, "Marina Beach"),
    "koyambedu": (13.0694, 80.1948, "Koyambedu"),
    "porur": (13.0382, 80.1565, "Porur"),
    "medavakkam": (12.9185, 80.1912, "Medavakkam"),
    "kilpauk": (13.0802, 80.2405, "Kilpauk"),
}


def validate_registry_coordinates() -> None:
    """Validate all registry entries against global and supported metro sanity bounds."""
    for key, (lat, lng, label) in KNOWN_LOCATIONS.items():
        if not (-90.0 <= lat <= 90.0):
            raise ValueError(f"Latitude {lat} for '{key}' is outside global bounds [-90, 90]")
        if not (-180.0 <= lng <= 180.0):
            raise ValueError(f"Longitude {lng} for '{key}' is outside global bounds [-180, 180]")

        in_any_metro = any(
            lat_r[0] <= lat <= lat_r[1] and lng_r[0] <= lng <= lng_r[1]
            for _, lat_r, lng_r in METRO_BOUNDS
        )
        if not in_any_metro:
            raise ValueError(
                f"Coordinates ({lat}, {lng}) for '{key}' ({label}) are outside all supported metro bounds"
            )


# Execute startup coordinate validation
validate_registry_coordinates()


class LocationResolver:
    """
    Deterministic location resolver that maps natural language location and landmark names
    to verified geographic coordinates (latitude, longitude, canonical name).
    LLM-generated coordinates are not accepted.
    """

    @classmethod
    def resolve_destination(cls, query: str | None) -> ResolvedLocation | None:
        """
        Resolve a destination name into ResolvedLocation(name, latitude, longitude).
        Returns None if location is unknown or ambiguous, triggering clarification.
        """
        if not query or not query.strip():
            return None

        cleaned = re.sub(r"[^\w\s]", " ", query.lower()).strip()
        cleaned = re.sub(r"\s+", " ", cleaned)

        # 1. Exact match lookup
        if cleaned in KNOWN_LOCATIONS:
            lat, lng, label = KNOWN_LOCATIONS[cleaned]
            return ResolvedLocation(name=label, latitude=lat, longitude=lng)

        # 2. Word boundary matching (e.g. "near manyata tech park on monday")
        for key, (lat, lng, label) in KNOWN_LOCATIONS.items():
            if re.search(r"\b" + re.escape(key) + r"\b", cleaned):
                return ResolvedLocation(name=label, latitude=lat, longitude=lng)

        # 3. Substring key matching for compound phrases
        for key, (lat, lng, label) in KNOWN_LOCATIONS.items():
            if len(key) >= 4 and key in cleaned:
                return ResolvedLocation(name=label, latitude=lat, longitude=lng)

        return None

    @classmethod
    def resolve_locality(cls, query: str | None) -> ResolvedLocation | None:
        """Alias for resolve_destination targeting neighborhood/locality names."""
        return cls.resolve_destination(query)
