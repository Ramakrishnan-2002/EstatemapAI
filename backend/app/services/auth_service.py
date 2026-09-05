from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ValidationException,
)
from app.core.logging import logger
from app.core.security import create_access_token, hash_password, verify_password
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest
from app.schemas.user import UserCreate


class AuthService:
    """
    Service handling user registration, authentication, token issuance,
    and authorization ownership checks.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.user_repo = UserRepository(session)

    async def register(self, user_in: UserCreate) -> User:
        """
        Register a new user account with secure password hashing.
        Handles race conditions on unique email constraint atomically.
        """
        # Pre-check email existence for cleaner error message
        existing = await self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ValidationException(
                message="A user with this email already exists.",
                details={"field": "email"},
            )

        password_hash = hash_password(user_in.password)

        try:
            user = await self.user_repo.create(
                email=user_in.email,
                hashed_password=password_hash,
                full_name=user_in.full_name,
            )
            await self.session.commit()
            logger.info("User successfully registered | user_id=%s email=%s", user.id, user.email)
            return user
        except IntegrityError as e:
            await self.session.rollback()
            logger.warning("Registration race condition caught on email=%s", user_in.email)
            raise ValidationException(
                message="A user with this email already exists.",
                details={"field": "email"},
            ) from e

    async def authenticate(self, login_in: LoginRequest) -> tuple[str, User]:
        """
        Authenticate user credentials and issue a signed JWT access token.
        Guards against user enumeration by returning identical error responses.
        """
        user = await self.user_repo.get_by_email(login_in.email)

        # Constant-time-like rejection for non-existent users or invalid passwords
        if not user or not verify_password(login_in.password, user.hashed_password):
            logger.warning("Failed login attempt for email=%s", login_in.email)
            raise AuthenticationException("Invalid email or password.")

        if not user.is_active:
            logger.warning("Login attempt for inactive user | user_id=%s", user.id)
            raise AuthenticationException("User account is inactive. Please contact support.")

        access_token = create_access_token(subject=str(user.id))
        logger.info("User successfully authenticated | user_id=%s", user.id)
        return access_token, user

    @staticmethod
    def ensure_ownership(resource_owner_id: int, current_user_id: int) -> None:
        """
        Verify that the authenticated user is the owner of the given resource.
        Raises AuthorizationException on mismatch.
        """
        if resource_owner_id != current_user_id:
            logger.warning(
                "Authorization mismatch | resource_owner=%s current_user=%s",
                resource_owner_id,
                current_user_id,
            )
            raise AuthorizationException(
                "You do not have permission to access or modify this resource."
            )
