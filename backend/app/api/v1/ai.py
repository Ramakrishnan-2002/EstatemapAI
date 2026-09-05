from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.rate_limit import RateLimiter
from app.schemas.ai import (
    AIExplanationRequest,
    AIExplanationResponse,
    AIHealthResponse,
    ParseSearchRequest,
    ParseSearchResponse,
)
from app.schemas.comparison import (
    AIComparisonResponse,
    PropertyComparisonRequest,
)
from app.schemas.conversational_search import (
    AskMapRequest,
    AskMapResponse,
)
from app.services.ai_service import AIService

router = APIRouter()


@router.get(
    "/health",
    response_model=AIHealthResponse,
    status_code=status.HTTP_200_OK,
    summary="AI Provider Health & Diagnostics",
    description=(
        "Check whether AI features are enabled, whether the configured local Ollama daemon is reachable, "
        "and whether the target model (llama3.2:3b) is downloaded and available."
    ),
)
async def get_ai_health(
    db: AsyncSession = Depends(get_db),
) -> AIHealthResponse:
    service = AIService(db)
    return await service.check_health()


@router.post(
    "/parse-search",
    response_model=ParseSearchResponse,
    status_code=status.HTTP_200_OK,
    summary="Natural Language Search Intent Extraction",
    description=(
        "Parse a natural language query into validated, bounded structured search criteria. "
        "Handles Indian real estate currency terminology (Lakhs, Crores) and POI category extraction. "
        "The model output is strictly validated by Pydantic and never directly executes SQL."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_AI_REQUESTS,
                window_seconds=settings.RATE_LIMIT_AI_WINDOW_SECONDS,
                scope="ai_parse_search",
                fail_open=True,
            )
        )
    ],
)
async def parse_search_intent(
    request: ParseSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> ParseSearchResponse:
    service = AIService(db)
    return await service.parse_search_intent(request.query)


@router.post(
    "/properties/{property_id}/explain",
    response_model=AIExplanationResponse,
    status_code=status.HTTP_200_OK,
    summary="Factual Property Match Explanation",
    description=(
        "Generate a concise, factual explanation for a property match. "
        "The backend collects verified property data, POI proximity, and commute duration into a bounded context. "
        "If the AI provider is offline or times out, gracefully falls back to deterministic rule-based explanations."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_AI_REQUESTS,
                window_seconds=settings.RATE_LIMIT_AI_WINDOW_SECONDS,
                scope="ai_property_explain",
                fail_open=True,
            )
        )
    ],
)
async def explain_property(
    property_id: int,
    request: AIExplanationRequest,
    db: AsyncSession = Depends(get_db),
) -> AIExplanationResponse:
    service = AIService(db)
    return await service.explain_property(property_id=property_id, request=request)


@router.post(
    "/properties/compare",
    response_model=AIComparisonResponse,
    status_code=status.HTTP_200_OK,
    summary="Grounded AI Multi-Property Comparison & Trade-off Narrative",
    description=(
        "Generate a grounded comparative narrative for 2 to 3 properties. "
        "The backend deterministically computes price differences, area deltas, commute times, "
        "and ranking contribution margins before invoking the AI layer. "
        "If the AI provider is offline or times out, gracefully falls back to deterministic summary statements."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_AI_REQUESTS,
                window_seconds=settings.RATE_LIMIT_AI_WINDOW_SECONDS,
                scope="ai_properties_compare",
                fail_open=True,
            )
        )
    ],
)
async def explain_property_comparison(
    request: PropertyComparisonRequest,
    db: AsyncSession = Depends(get_db),
) -> AIComparisonResponse:
    service = AIService(db)
    return await service.explain_comparison(request=request)


@router.post(
    "/ask-map",
    response_model=AskMapResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the Map — Conversational Search & Orchestration",
    description=(
        "Conversational search orchestrator for property discovery. "
        "Interprets natural language queries, extracts a validated state patch, applies mutations "
        "to the canonical search state, and executes deterministic PostGIS spatial filtering, "
        "commute calculations, POI enrichment, and ranking engines."
    ),
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_AI_REQUESTS,
                window_seconds=settings.RATE_LIMIT_AI_WINDOW_SECONDS,
                scope="ai_ask_map",
                fail_open=True,
            )
        )
    ],
)
async def ask_map(
    request: AskMapRequest,
    db: AsyncSession = Depends(get_db),
) -> AskMapResponse:
    service = AIService(db)
    return await service.ask_map(request=request)
