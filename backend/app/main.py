from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1 import api_router
from app.api.v1.health import router as health_router
from app.cache.redis import close_redis_connection
from app.core.config import settings
from app.core.exception_handlers import (
    app_exception_handler,
    http_exception_handler,
    sqlalchemy_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.core.exceptions import AppException
from app.core.logging import logger, setup_logging
from app.core.middleware import RequestIDMiddleware
from app.db.session import close_db_connection


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup phase
    setup_logging(settings.ENVIRONMENT)
    logger.info("Starting up %s in %s environment", settings.PROJECT_NAME, settings.ENVIRONMENT)

    # Auto-seed database if empty in development
    if settings.ENVIRONMENT != "test":
        try:
            from app.db.seed_all import seed_all
            await seed_all()
        except Exception as e:
            logger.warning("Auto-seed during startup encountered error (skipping): %s", e)

    yield
    # Shutdown phase
    logger.info("Shutting down %s...", settings.PROJECT_NAME)
    await close_db_connection()
    await close_redis_connection()
    logger.info("Shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Location-first real estate discovery powered by FastAPI, PostGIS, AI and mapcn",
    version="0.1.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Custom Middlewares (Order matters: outermost first)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Centralized Exception Handlers
app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Health Endpoints (mounted at root /health for K8s/Docker and under /api/v1/health)
app.include_router(health_router, prefix="/health")

# Master API v1 Router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to EstateMap AI API",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": "/health",
    }
