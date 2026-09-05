import pytest
from fastapi import APIRouter
from httpx import AsyncClient

from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ExternalServiceException,
    ResourceNotFoundException,
    ValidationException,
)
from app.main import app

# Dummy test router to verify exception handler responses
dummy_router = APIRouter(prefix="/test-exceptions")


@dummy_router.get("/not-found")
async def trigger_not_found():
    raise ResourceNotFoundException(resource="Property", identifier=42)


@dummy_router.get("/auth-error")
async def trigger_auth_error():
    raise AuthenticationException("Invalid token provided")


@dummy_router.get("/forbidden")
async def trigger_forbidden():
    raise AuthorizationException("Admin privileges required")


@dummy_router.get("/validation-error")
async def trigger_validation_error():
    raise ValidationException("Field 'price' must be greater than zero", details={"field": "price"})


@dummy_router.get("/external-error")
async def trigger_external_error():
    raise ExternalServiceException(service_name="Gemini", message="Rate limit exceeded")


@dummy_router.get("/unhandled-error")
async def trigger_unhandled():
    raise RuntimeError("Simulated unexpected crash")


app.include_router(dummy_router)


@pytest.mark.asyncio
async def test_resource_not_found_exception(async_client: AsyncClient):
    response = await async_client.get("/test-exceptions/not-found")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert "Property '42' was not found" in data["error"]["message"]
    assert data["error"]["details"]["resource"] == "Property"
    assert data["error"]["request_id"] != ""
    assert response.headers.get("X-Request-ID") == data["error"]["request_id"]


@pytest.mark.asyncio
async def test_authentication_exception(async_client: AsyncClient):
    response = await async_client.get("/test-exceptions/auth-error")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHENTICATION_FAILED"
    assert data["error"]["message"] == "Invalid token provided"
    assert "request_id" in data["error"]


@pytest.mark.asyncio
async def test_authorization_exception(async_client: AsyncClient):
    response = await async_client.get("/test-exceptions/forbidden")
    assert response.status_code == 403
    data = response.json()
    assert data["error"]["code"] == "FORBIDDEN"
    assert "request_id" in data["error"]


@pytest.mark.asyncio
async def test_validation_exception(async_client: AsyncClient):
    response = await async_client.get("/test-exceptions/validation-error")
    assert response.status_code == 422
    data = response.json()
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["details"]["field"] == "price"


@pytest.mark.asyncio
async def test_external_service_exception(async_client: AsyncClient):
    response = await async_client.get("/test-exceptions/external-error")
    assert response.status_code == 502
    data = response.json()
    assert data["error"]["code"] == "EXTERNAL_SERVICE_ERROR"
    assert "[Gemini]" in data["error"]["message"]


@pytest.mark.asyncio
async def test_unhandled_exception(async_client: AsyncClient):
    response = await async_client.get("/test-exceptions/unhandled-error")
    assert response.status_code == 500
    data = response.json()
    assert data["error"]["code"] == "INTERNAL_SERVER_ERROR"
    # Verify internal exception details are NOT leaked
    assert "Simulated unexpected crash" not in data["error"]["message"]
    assert "request_id" in data["error"]


@pytest.mark.asyncio
async def test_404_standard_http_exception(async_client: AsyncClient):
    response = await async_client.get("/non-existent-endpoint-12345")
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"
    assert "request_id" in data["error"]
