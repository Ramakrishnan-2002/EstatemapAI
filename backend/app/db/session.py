from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.logging import logger

# Initialize Async SQLAlchemy Engine with environment-aware pooling
engine_kwargs: dict[str, Any] = {
    "echo": (settings.ENVIRONMENT == "development"),
    "future": True,
}

if settings.ENVIRONMENT == "test":
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_size"] = 10
    engine_kwargs["max_overflow"] = 20
    engine_kwargs["pool_recycle"] = 3600

engine = create_async_engine(settings.DATABASE_URL, **engine_kwargs)

# Async Session Factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that yields an async database session per request.
    Rolls back transaction on unhandled exception and guarantees session closure.
    """
    async with async_session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def close_db_connection() -> None:
    """Dispose of database engine connection pools on application shutdown."""
    logger.info("Disposing PostgreSQL connection pool...")
    await engine.dispose()
    logger.info("PostgreSQL connection pool disposed.")


async def check_db_health() -> dict[str, Any]:
    """
    Verify PostgreSQL and PostGIS connectivity and versions.
    Opens a standalone session to avoid loop-affinity issues during tests.
    Does not expose sensitive credentials.
    """
    try:
        async with async_session_factory() as session:
            # Check basic PostgreSQL connectivity
            await session.execute(text("SELECT 1;"))

            # Check PostGIS extension & version
            postgis_version: str | None = None
            try:
                result = await session.execute(text("SELECT PostGIS_Version();"))
                row = result.scalar_one_or_none()
                postgis_version = str(row) if row else "unknown"
            except Exception as pe:
                logger.warning("PostGIS extension check failed: %s", pe)
                postgis_version = "not_installed"

            return {
                "status": "healthy",
                "database": "postgresql",
                "postgis": postgis_version,
            }
    except Exception as e:
        logger.error("Database health check failed: %s", str(e))
        return {
            "status": "unhealthy",
            "database": "postgresql",
            "error": "Database connection failed",
        }
