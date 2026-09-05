from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
async def favorites_status():
    return {"module": "favorites", "status": "ready"}
