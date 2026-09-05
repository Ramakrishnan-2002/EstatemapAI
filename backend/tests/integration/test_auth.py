from datetime import timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthorizationException
from app.core.security import create_access_token
from app.models.user import User
from app.services.auth_service import AuthService


@pytest.fixture(autouse=True)
async def cleanup_users_table(db_session: AsyncSession):
    """Clean up test users without deleting seed demo user and properties."""
    await db_session.execute(text("DELETE FROM users WHERE email NOT IN ('demo@estatemap.ai');"))
    await db_session.commit()
    yield
    await db_session.execute(text("DELETE FROM users WHERE email NOT IN ('demo@estatemap.ai');"))
    await db_session.commit()


@pytest.mark.asyncio
async def test_register_user_success(async_client: AsyncClient, db_session: AsyncSession):
    email = "test.agent@estatemap.ai"
    payload = {
        "email": email,
        "password": "SecurePassword123!",
        "full_name": "Test Agent",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()

    assert data["email"] == email
    assert data["full_name"] == "Test Agent"
    assert data["is_active"] is True
    assert "id" in data
    # Ensure sensitive fields are NEVER leaked
    assert "hashed_password" not in data
    assert "password" not in data
    assert "X-Request-ID" in response.headers

    # Verify password is truly hashed in database
    await db_session.rollback()
    stmt = select(User).where(User.email == email)
    result = await db_session.execute(stmt)
    user_in_db = result.scalar_one()
    assert user_in_db is not None
    assert user_in_db.hashed_password != "SecurePassword123!"


@pytest.mark.asyncio
async def test_register_duplicate_email(async_client: AsyncClient):
    payload = {
        "email": "duplicate@estatemap.ai",
        "password": "SecurePassword123!",
        "full_name": "Duplicate User",
    }
    # First registration
    res1 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res1.status_code == 201

    # Second registration with same email
    res2 = await async_client.post("/api/v1/auth/register", json=payload)
    assert res2.status_code == 422
    data = res2.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "already exists" in data["error"]["message"].lower()


@pytest.mark.asyncio
async def test_register_email_normalization(async_client: AsyncClient, db_session: AsyncSession):
    raw_email = "   Normalized.User@EstateMap.AI   "
    expected_email = "normalized.user@estatemap.ai"
    payload = {
        "email": raw_email,
        "password": "SecurePassword123!",
        "full_name": "Normalized User",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == expected_email


@pytest.mark.asyncio
async def test_register_weak_password_validation(async_client: AsyncClient):
    payload = {
        "email": "weakpass@estatemap.ai",
        "password": "123",  # Less than 8 chars
        "full_name": "Weak Password User",
    }
    response = await async_client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_login_success(async_client: AsyncClient):
    email = "login.success@estatemap.ai"
    password = "CorrectPassword123!"

    # Register first
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Login User"},
    )

    # Login
    response = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == email
    assert "hashed_password" not in data["user"]


@pytest.mark.asyncio
async def test_login_invalid_password_and_nonexistent_email(
    async_client: AsyncClient,
):
    # Nonexistent user
    res1 = await async_client.post(
        "/api/v1/auth/login",
        json={
            "email": "nonexistent@estatemap.ai",
            "password": "AnyPassword123!",
        },
    )
    assert res1.status_code == 401
    assert res1.json()["error"]["code"] == "AUTHENTICATION_FAILED"
    assert "Invalid email or password" in res1.json()["error"]["message"]

    # Register user
    email = "wrongpass@estatemap.ai"
    await async_client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": "CorrectPassword123!",
            "full_name": "User",
        },
    )

    # Wrong password -> Identical error message to prevent user enumeration
    res2 = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": "WrongPassword123!"},
    )
    assert res2.status_code == 401
    assert res2.json()["error"]["code"] == "AUTHENTICATION_FAILED"
    assert "Invalid email or password" in res2.json()["error"]["message"]


@pytest.mark.asyncio
async def test_current_user_me_endpoint(async_client: AsyncClient):
    email = "me.profile@estatemap.ai"
    password = "MyPassword123!"

    # Register & Login
    await async_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Me Profile"},
    )
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": password},
    )
    token = login_res.json()["access_token"]

    # Authenticated request to /users/me
    response = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert data["full_name"] == "Me Profile"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_current_user_unauthenticated_and_expired_token(
    async_client: AsyncClient,
):
    # No token provided
    res1 = await async_client.get("/api/v1/users/me")
    assert res1.status_code == 401
    assert res1.json()["error"]["code"] == "AUTHENTICATION_FAILED"

    # Expired token
    expired_token = create_access_token(subject=1, expires_delta=timedelta(seconds=-10))
    res2 = await async_client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert res2.status_code == 401
    assert "expired" in res2.json()["error"]["message"].lower()


@pytest.mark.asyncio
async def test_ownership_authorization_helper():
    # Matching owner and user -> Passes without exception
    AuthService.ensure_ownership(resource_owner_id=5, current_user_id=5)

    # Mismatched owner and user -> Raises AuthorizationException (403)
    with pytest.raises(AuthorizationException) as exc_info:
        AuthService.ensure_ownership(resource_owner_id=5, current_user_id=10)
    assert exc_info.value.status_code == 403
    assert exc_info.value.code == "FORBIDDEN"
