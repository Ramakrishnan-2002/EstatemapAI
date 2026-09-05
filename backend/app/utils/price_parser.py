from __future__ import annotations

import re


class IndianPriceParser:
    """
    Deterministic parser for Indian real-estate currency notation.
    Accurately converts colloquial terms (Lakh, Crore, K, commas, symbols)
    into standard numeric INR (float).
    """

    LAKH_MULTIPLIER = 100_000.0
    CRORE_MULTIPLIER = 10_000_000.0
    THOUSAND_MULTIPLIER = 1_000.0

    # Match expressions like "1.2 crore", "75 lakh", "80L", "1.5cr", "50k", "₹70L", "Rs. 85 Lakhs"
    _CRORE_PATTERN = re.compile(
        r"(?:(?:rs\.?|inr|₹)\s*)?([0-9]+(?:\.[0-9]+)?)\s*(?:cr(?:ore)?s?)\b",
        re.IGNORECASE,
    )
    _LAKH_PATTERN = re.compile(
        r"(?:(?:rs\.?|inr|₹)\s*)?([0-9]+(?:\.[0-9]+)?)\s*(?:l(?:akh|ac)?s?)\b",
        re.IGNORECASE,
    )
    _THOUSAND_PATTERN = re.compile(
        r"(?:(?:rs\.?|inr|₹)\s*)?([0-9]+(?:\.[0-9]+)?)\s*(?:k|thousand|thousands)\b",
        re.IGNORECASE,
    )
    _RAW_NUMERIC_PATTERN = re.compile(
        r"(?:(?:rs\.?|inr|₹)\s*)?([0-9]{1,3}(?:,[0-9]{2,3})*(?:\.[0-9]+)?|[0-9]+(?:\.[0-9]+)?)"
    )

    @classmethod
    def parse_inr(cls, raw: str | int | float | None) -> float | None:
        """
        Parse any Indian real-estate price string or number into standard INR float.
        Returns None if input is empty or invalid.
        """
        if raw is None:
            return None
        if isinstance(raw, int | float):
            return float(raw) if raw >= 0 else None

        text = str(raw).strip()
        if not text:
            return None

        # 1. Check Crore notation
        crore_match = cls._CRORE_PATTERN.search(text)
        if crore_match:
            val = float(crore_match.group(1))
            return round(val * cls.CRORE_MULTIPLIER, 2)

        # 2. Check Lakh notation
        lakh_match = cls._LAKH_PATTERN.search(text)
        if lakh_match:
            val = float(lakh_match.group(1))
            return round(val * cls.LAKH_MULTIPLIER, 2)

        # 3. Check Thousand / K notation
        thousand_match = cls._THOUSAND_PATTERN.search(text)
        if thousand_match:
            val = float(thousand_match.group(1))
            return round(val * cls.THOUSAND_MULTIPLIER, 2)

        # 4. Check Raw numeric with or without commas (e.g. 70,00,000 or 7000000)
        # Clean currency symbols
        cleaned = re.sub(r"[₹RsINRinrs\.\s]", "", text)
        cleaned = cleaned.replace(",", "")
        try:
            val = float(cleaned)
            return round(val, 2) if val >= 0 else None
        except ValueError:
            return None
