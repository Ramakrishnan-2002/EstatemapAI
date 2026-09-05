import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_request_id_generated_if_missing(async_client: AsyncClient):
    response = await async_client.get("/health/live")
    assert response.status_code == 200
    req_id = response.headers.get("X-Request-ID")
    assert req_id is not None
    assert len(req_id) >= 32  # UUID4 length with hyphens is 36


@pytest.mark.asyncio
async def test_request_id_preserved_when_provided(async_client: AsyncClient):
    custom_id = "custom-test-correlation-id-999"
    response = await async_client.get("/health/live", headers={"X-Request-ID": custom_id})
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID") == custom_id
