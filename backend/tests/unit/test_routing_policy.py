import pytest

from app.ai.routing_policy import AIRoutingPolicy
from app.core.exceptions import AIProviderConfigurationException


def test_routing_policy_core_property_queries():
    # 1. Simple 2 BHK in Indiranagar
    q1 = "2 BHK in Indiranagar"
    p1 = AIRoutingPolicy.profile_intent_query(q1)
    assert p1.is_complex is False
    assert p1.complexity_score < 3
    order1, _ = AIRoutingPolicy.select_providers(p1, configured_mode="auto")
    assert order1 == ["ollama", "gemini"]

    # 2. 2 BHK apartment under 80 lakh in Indiranagar (Ordinary filters remain local)
    q2 = "2 BHK apartment under 80 lakh in Indiranagar"
    p2 = AIRoutingPolicy.profile_intent_query(q2)
    assert p2.is_complex is False
    assert p2.complexity_score < 3
    order2, _ = AIRoutingPolicy.select_providers(p2, configured_mode="auto")
    assert order2 == ["ollama", "gemini"]

    # 3. Flat in Koramangala near hospital (Single POI remains local)
    q3 = "flat in Koramangala near hospital"
    p3 = AIRoutingPolicy.profile_intent_query(q3)
    assert p3.is_complex is False
    assert p3.complexity_score < 3
    order3, _ = AIRoutingPolicy.select_providers(p3, configured_mode="auto")
    assert order3 == ["ollama", "gemini"]


def test_routing_policy_complex_queries():
    # Multi-POI + Commute target in Whitefield
    q_complex = "3 BHK villa in Whitefield under 2.5 Cr near hospital, school, metro with commute to Electronic City"
    p_complex = AIRoutingPolicy.profile_intent_query(q_complex)
    assert p_complex.is_complex is True
    assert p_complex.has_commute_target is True
    assert p_complex.has_multiple_pois is True
    assert p_complex.complexity_score >= 3
    order_complex, reason = AIRoutingPolicy.select_providers(p_complex, configured_mode="auto")
    assert order_complex[0] == "gemini"
    assert order_complex[1] == "ollama"
    assert "complex" in reason.lower()

    # Long multi-clause query (> 100 chars)
    long_q = "Looking for a spacious modern property for my family with good connectivity, ample sunlight, nearby gardens, and peaceful neighborhood"
    p_long = AIRoutingPolicy.profile_intent_query(long_q)
    assert p_long.query_length > 100
    assert p_long.complexity_score >= 3
    order_long, _ = AIRoutingPolicy.select_providers(p_long, configured_mode="auto")
    assert order_long[0] == "gemini"


def test_routing_policy_static_modes():
    profile = AIRoutingPolicy.profile_intent_query("2 BHK in Indiranagar")

    p_ollama, r_ollama = AIRoutingPolicy.select_providers(profile, configured_mode="ollama")
    assert p_ollama == ["ollama"]
    assert "ollama" in r_ollama.lower()

    p_gemini, r_gemini = AIRoutingPolicy.select_providers(profile, configured_mode="gemini")
    assert p_gemini == ["gemini"]
    assert "gemini" in r_gemini.lower()

    p_mock, r_mock = AIRoutingPolicy.select_providers(profile, configured_mode="mock")
    assert p_mock == ["mock"]
    assert "mock" in r_mock.lower()


def test_routing_policy_invalid_mode_fails_loudly():
    profile = AIRoutingPolicy.profile_intent_query("2 BHK in Indiranagar")
    with pytest.raises(AIProviderConfigurationException):
        AIRoutingPolicy.select_providers(profile, configured_mode="gemnii")


def test_routing_policy_explanation_context():
    # Simple context (<= 1 POI, no commute)
    simple_ctx = {
        "property": {"bedrooms": 2, "price_inr": 8000000},
        "location_intelligence_3km": {"hospital": {"nearest_distance_km": 1.2, "count_nearby": 1}},
        "commute": None,
    }
    p_simple = AIRoutingPolicy.profile_explanation_context(simple_ctx)
    assert p_simple.is_complex is False
    order_simple, _ = AIRoutingPolicy.select_providers(p_simple, configured_mode="auto")
    assert order_simple == ["ollama", "gemini"]

    # Complex context (multiple POIs + commute)
    complex_ctx = {
        "property": {"bedrooms": 4, "price_inr": 35000000},
        "location_intelligence_3km": {
            "hospital": {"nearest_distance_km": 0.8, "count_nearby": 4},
            "school": {"nearest_distance_km": 1.5, "count_nearby": 2},
            "transit": {"nearest_distance_km": 0.4, "count_nearby": 1},
        },
        "commute": {"destination": "Electronic City", "distance_km": 18.5, "duration_minutes": 35},
    }
    p_complex = AIRoutingPolicy.profile_explanation_context(complex_ctx)
    assert p_complex.is_complex is True
    order_complex, _ = AIRoutingPolicy.select_providers(p_complex, configured_mode="auto")
    assert order_complex[0] == "gemini"
