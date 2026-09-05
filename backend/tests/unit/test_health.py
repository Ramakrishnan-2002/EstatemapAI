import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_live_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "EstateMap" in data["service"]
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_health_ready_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"]["status"] == "healthy"
    assert data["database"]["database"] == "postgresql"
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_health_diagnostics_endpoint(async_client: AsyncClient):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert data["service"] == "EstateMap AI"
    assert "database" in data
    assert "cache" in data
    assert "X-Request-ID" in response.headers


@pytest.mark.asyncio
async def test_api_v1_health_endpoints(async_client: AsyncClient):
    res_live = await async_client.get("/api/v1/health/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"] == "alive"

    res_ready = await async_client.get("/api/v1/health/ready")
    assert res_ready.status_code == 200
    assert res_ready.json()["status"] == "ready"
