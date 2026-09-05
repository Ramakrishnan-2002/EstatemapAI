from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationException
from app.core.security import decode_access_token
from app.db.session import async_session_factory
from app.models.user import User
from app.repositories.user_repository import UserRepository

# HTTPBearer security scheme for extracting Bearer tokens from Authorization header
http_bearer_scheme = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields an async database session per request."""
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(http_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Dependency that authenticates the caller via Bearer JWT.
    Validates token signature, expiration, and retrieves user from database.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationException("Not authenticated. Bearer token required.")

    token = credentials.credentials
    payload = decode_access_token(token)

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationException("Token missing subject identifier.")

    try:
        user_id = int(user_id_str)
    except ValueError as e:
        raise AuthenticationException("Invalid token subject format.") from e

    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)

    if user is None:
        raise AuthenticationException("User corresponding to this token does not exist.")

    if not user.is_active:
        raise AuthenticationException("User account is inactive.")

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Dependency ensuring the authenticated user is active."""
    if not current_user.is_active:
        raise AuthenticationException("User account is inactive.")
    return current_user
