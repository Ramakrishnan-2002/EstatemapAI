from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.dependencies import get_db
from app.core.rate_limit import RateLimiter
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserCreate, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_AUTH_REQUESTS,
                window_seconds=settings.RATE_LIMIT_AUTH_WINDOW_SECONDS,
                scope="auth_register",
                fail_open=False,
            )
        )
    ],
)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Create a new user account with validated credentials.
    Returns safe user information without exposing password hashes.
    """
    auth_service = AuthService(db)
    user = await auth_service.register(user_in)
    return UserResponse.model_validate(user)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User login with email and password",
    dependencies=[
        Depends(
            RateLimiter(
                requests_limit=settings.RATE_LIMIT_AUTH_REQUESTS,
                window_seconds=settings.RATE_LIMIT_AUTH_WINDOW_SECONDS,
                scope="auth_login",
                fail_open=False,
            )
        )
    ],
)
async def login(
    login_in: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> Token:
    """
    Authenticate using email and password.
    Returns a signed JWT access token and user metadata.
    """
    auth_service = AuthService(db)
    access_token, user = await auth_service.authenticate(login_in)
    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


@router.get("/status")
async def auth_status():
    return {"module": "auth", "status": "ready"}
