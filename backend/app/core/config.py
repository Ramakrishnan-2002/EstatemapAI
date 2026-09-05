from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="ignore",
    )

    # General
    ENVIRONMENT: Literal["development", "staging", "production", "test"] = "development"
    PROJECT_NAME: str = "EstateMap AI"
    API_V1_STR: str = "/api/v1"

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://estatemap:estatemap_dev_password@localhost:5432/estatemap_db"
    )

    # Redis & Caching Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_ENABLED: bool = True
    CACHE_COORDINATE_PRECISION: int = 4  # ~11m precision
    CACHE_ROUTE_TTL_SECONDS: int = 600  # 10 minutes
    CACHE_POI_TTL_SECONDS: int = 1800  # 30 minutes
    CACHE_MAP_TTL_SECONDS: int = 120  # 2 minutes
    CACHE_RANKING_TTL_SECONDS: int = 300  # 5 minutes

    # Rate Limiting Configuration
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_DEFAULT_REQUESTS: int = 100
    RATE_LIMIT_DEFAULT_WINDOW_SECONDS: int = 60
    RATE_LIMIT_RANKED_SEARCH_REQUESTS: int = 20
    RATE_LIMIT_RANKED_SEARCH_WINDOW_SECONDS: int = 60
    RATE_LIMIT_COMMUTE_REQUESTS: int = 30
    RATE_LIMIT_COMMUTE_WINDOW_SECONDS: int = 60
    RATE_LIMIT_AUTH_REQUESTS: int = 10
    RATE_LIMIT_AUTH_WINDOW_SECONDS: int = 60
    RATE_LIMIT_AI_REQUESTS: int = 15
    RATE_LIMIT_AI_WINDOW_SECONDS: int = 60
    RATE_LIMIT_FAIL_OPEN: bool = True

    # Security
    JWT_SECRET: str = "insecure_dev_jwt_secret_key_change_in_production_min_32_bytes_long"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Routing & Commute Configuration
    ROUTING_PROVIDER: Literal["mock", "osrm"] = "mock"
    OSRM_BASE_URL: str = "http://router.project-osrm.org"
    ROUTING_CACHE_TTL_SECONDS: int = 600
    MAX_COMMUTE_DESTINATIONS: int = 5
    MAX_COMMUTE_COMPARE_PROPERTIES: int = 10

    # Ranking & Recommendation Configuration
    MAX_RANKING_CANDIDATES: int = 50
    RANKING_ALGORITHM_VERSION: str = "weighted_deterministic_v1"

    # AI Configuration (Phase 11 & Phase 12 Multi-Provider)
    AI_ENABLED: bool = True
    AI_PROVIDER: Literal["ollama", "gemini", "mock", "auto"] = "auto"
    AI_PRIMARY_PROVIDER: Literal["ollama", "gemini", "mock"] = "ollama"
    AI_FALLBACK_PROVIDER: Literal["ollama", "gemini", "mock", "none"] = "gemini"
    AI_ROUTING_COMPLEXITY_THRESHOLD: int = 3
    AI_TOTAL_TIMEOUT_SECONDS: float = 35.0

    # Gemini Hosted Provider Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.6-flash"
    GEMINI_TIMEOUT_SECONDS: float = 20.0
    GEMINI_MAX_OUTPUT_TOKENS: int = 4096
    GEMINI_TEMPERATURE_INTENT: float = 0.0
    GEMINI_TEMPERATURE_EXPLANATION: float = 0.2

    # Local Ollama Provider Configuration
    OLLAMA_BASE_URL: str = "http://host.docker.internal:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_TIMEOUT_SECONDS: float = 20.0
    OLLAMA_KEEP_ALIVE: str = "5m"

    # AI Prompt Templates
    AI_PROMPT_VERSION_INTENT: str = "search-intent:v1"
    AI_PROMPT_VERSION_EXPLANATION: str = "property-explanation:v1"


settings = Settings()
