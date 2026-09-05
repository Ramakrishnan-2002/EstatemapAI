from fastapi import APIRouter

from app.api.v1 import (
    ai,
    auth,
    commute,
    favorites,
    health,
    maps,
    pois,
    properties,
    recommendations,
    search,
    users,
)

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(properties.router, prefix="/properties", tags=["Properties"])
api_router.include_router(commute.router, prefix="/commute", tags=["Commute"])
api_router.include_router(search.router, prefix="/search", tags=["Search"])
api_router.include_router(maps.router, prefix="/maps", tags=["Maps"])
api_router.include_router(pois.router, prefix="/pois", tags=["POIs"])
api_router.include_router(favorites.router, prefix="/favorites", tags=["Favorites"])
api_router.include_router(
    recommendations.router, prefix="/recommendations", tags=["Recommendations"]
)
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
