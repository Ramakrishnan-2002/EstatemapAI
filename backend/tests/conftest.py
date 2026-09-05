import os
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
import redis.asyncio as aioredis
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

# Set test environment
os.environ["ENVIRONMENT"] = "test"

from app.core.config import settings

settings.ROUTING_PROVIDER = "mock"
from app.main import app  # noqa: E402


@pytest_asyncio.fixture(loop_scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async test HTTP client with ASGI transport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture(loop_scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provides an isolated transactional database session with NullPool for integration tests."""
    engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        future=True,
    )
    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session
    await engine.dispose()


@pytest_asyncio.fixture(loop_scope="function")
async def redis_conn() -> AsyncGenerator[aioredis.Redis, None]:
    """Provides a fresh, isolated Redis connection for integration tests."""
    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        yield client
    finally:
        await client.aclose()


@pytest_asyncio.fixture(loop_scope="function", autouse=True)
async def clear_redis_ratelimit_and_cache():
    """Ensure clean Redis cache and rate limit counters between each test."""
    import app.cache.redis as app_redis

    if app_redis.redis_client is not None:
        try:
            await app_redis.redis_client.aclose()
        except Exception:
            pass
        app_redis.redis_client = None

    client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    try:
        keys = await client.keys("estatemap:*")
        if keys:
            await client.delete(*keys)
    except Exception:
        pass
    finally:
        await client.aclose()

    yield

    if app_redis.redis_client is not None:
        try:
            await app_redis.redis_client.aclose()
        except Exception:
            pass
        app_redis.redis_client = None


@pytest.fixture(scope="session", autouse=True)
def restore_seed_data_after_tests():
    """Ensure database has standard demo listings restored after test execution completes."""
    yield
    try:
        import asyncio

        from app.db.seed_all import seed_all

        asyncio.run(seed_all())
    except Exception:
        pass
