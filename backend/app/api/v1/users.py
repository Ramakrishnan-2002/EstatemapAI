from fastapi import APIRouter, Depends, status

from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current authenticated user profile",
)
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Retrieve user metadata and profile for the authenticated caller.
    Guaranteed not to leak password hashes.
    """
    return UserResponse.model_validate(current_user)


@router.get("/status")
async def users_status():
    return {"module": "users", "status": "ready"}
