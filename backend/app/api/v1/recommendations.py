from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.rate_limit import RateLimiter
from app.schemas.ranking import RankedSearchRequest, RankedSearchResponse
from app.services.ranking_service import RankingService

router = APIRouter()


@router.get("/status")
async def recommendations_status():
    return {"module": "recommendations", "status": "ready"}


@router.post(
    "/ranked",
    response_model=RankedSearchResponse,
    summary="Deterministic Property Recommendations",
    description="Score and rank eligible properties deterministically based on user preferences and constraints.",
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_RANKED_SEARCH_REQUESTS,
                window_seconds=settings.RATE_LIMIT_RANKED_SEARCH_WINDOW_SECONDS,
                scope="recommendations_ranked",
            )
        )
    ],
)
async def get_ranked_recommendations(
    payload: RankedSearchRequest,
    db: AsyncSession = Depends(get_db),
) -> RankedSearchResponse:
    service = RankingService(db)
    return await service.rank_properties(payload)
