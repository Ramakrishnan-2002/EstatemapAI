from fastapi import APIRouter, Response, status

from app.cache.redis import check_redis_health
from app.core.config import settings
from app.db.session import check_db_health

router = APIRouter()


@router.get("/live", tags=["Health"], summary="Liveness Probe")
async def liveness_probe() -> dict[str, str]:
    """
    Kubernetes / Docker liveness probe.
    Confirms whether the Python/FastAPI process is alive.
    Does not probe downstream dependencies.
    """
    return {
        "status": "alive",
        "service": settings.PROJECT_NAME,
    }


@router.get("/ready", tags=["Health"], summary="Readiness Probe")
async def readiness_probe(response: Response) -> dict[str, object]:
    """
    Kubernetes / Docker readiness probe.
    Verifies that critical dependencies (PostgreSQL + PostGIS) are healthy.
    Returns 503 if the database is unreachable.
    """
    db_health = await check_db_health()
    redis_health = await check_redis_health()

    is_db_healthy = db_health.get("status") == "healthy"
    overall_status = "ready" if is_db_healthy else "not_ready"

    if not is_db_healthy:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": overall_status,
        "service": settings.PROJECT_NAME,
        "database": db_health,
        "cache": redis_health,
    }


@router.get("", tags=["Health"], summary="Overall Health Diagnostics")
async def health_diagnostics() -> dict[str, object]:
    """
    Concise overall diagnostic status for observability and health monitoring.
    """
    db_health = await check_db_health()
    redis_health = await check_redis_health()

    overall_status = "healthy"
    if db_health.get("status") != "healthy":
        overall_status = "unhealthy"
    elif redis_health.get("status") != "healthy":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": "0.1.0",
        "database": db_health,
        "cache": redis_health,
    }
