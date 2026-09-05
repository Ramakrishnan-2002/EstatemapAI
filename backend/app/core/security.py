from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.exceptions import AuthenticationException
from app.core.logging import logger

# CryptContext configured with Argon2 and Bcrypt fallback
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        logger.error("Error during password verification: %s", e)
        return False


def hash_password(password: str) -> str:
    """Generate a secure cryptographic hash for a plaintext password."""
    return pwd_context.hash(password)


# Backward compatibility alias
get_password_hash = hash_password


def create_access_token(
    subject: str | Any,
    expires_delta: timedelta | None = None,
    extra_claims: dict[str, Any] | None = None,
) -> str:
    """
    Generate a signed JWT access token.
    Claims: sub (subject/user_id), iat (issued at), exp (expiration), type ("access").
    """
    now = datetime.now(UTC)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload: dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    encoded_jwt = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any]:
    """
    Decode and validate a signed JWT access token.
    Raises AuthenticationException on malformed, expired, or invalid tokens.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise AuthenticationException("Invalid token type.")
        if not payload.get("sub"):
            raise AuthenticationException("Token missing subject identifier.")
        return payload
    except jwt.ExpiredSignatureError as e:
        raise AuthenticationException("Token has expired. Please log in again.") from e
    except jwt.InvalidTokenError as e:
        raise AuthenticationException(f"Invalid token: {e!s}") from e
    except Exception as e:
        logger.warning("Failed to decode token: %s", str(e))
        raise AuthenticationException("Could not validate credentials.") from e
