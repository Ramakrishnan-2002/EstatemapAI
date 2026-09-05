# EstateMap AI — Know Your Codebase Map

This document is the exhaustive directory of where every engineering concept, algorithm, business rule, and data model is implemented in the EstateMap AI repository.

---

## 1. Backend Code Map

| Engineering Capability | File Path | Key Functions / Classes / Symbols |
| :--- | :--- | :--- |
| **Application Lifespan & Startup Seeding** | `backend/app/main.py` | `lifespan(app: FastAPI)`, `create_app()` |
| **Application Configuration & Settings** | `backend/app/core/config.py` | `Settings`, `get_settings()` |
| **Database Async Session & Engine** | `backend/app/db/session.py` | `engine`, `async_session_factory`, `get_db()` |
| **Centralized Database Dependency** | `backend/app/core/dependencies.py` | `get_db()`, `get_current_user()`, `get_current_active_user()` |
| **Password Hashing & JWT Crypto** | `backend/app/core/security.py` | `verify_password()`, `get_password_hash()`, `create_access_token()`, `decode_access_token()` |
| **Sliding-Window Rate Limiter** | `backend/app/core/rate_limit.py` | `RateLimiter`, `RateLimitRule`, `check_rate_limit()` |
| **Request ID Middleware & Rate Limit Interceptor** | `backend/app/core/middleware.py` | `RequestIDMiddleware`, `RateLimitMiddleware` |
| **RFC 7807 Exception Handlers** | `backend/app/core/exception_handlers.py` | `app_exception_handler()`, `validation_exception_handler()`, `global_exception_handler()` |
| **Redis Async Connection & Client** | `backend/app/cache/redis.py` | `get_redis_pool()`, `close_redis_pool()` |
| **Redis Cache-Aside Service** | `backend/app/cache/cache_service.py` | `CacheService`, `get()`, `set()`, `delete_pattern()` |
| **Deterministic Cache Key Generators** | `backend/app/cache/cache_keys.py` | `commute_cache_key()`, `poi_intelligence_cache_key()`, `ranking_cache_key()` |
| **PostGIS Spatial GeoRepository** | `backend/app/repositories/geo_repository.py` | `GeoRepository`, `search_by_bbox()`, `search_by_radius()`, `get_nearby_pois()` |
| **Property CRUD Repository** | `backend/app/repositories/property_repository.py` | `PropertyRepository`, `create()`, `get_by_id()`, `list_with_filters()`, `update()`, `delete()` |
| **OSRM Road Routing Client** | `backend/app/services/routing_service.py` | `RoutingProvider`, `OSRMProvider`, `MockRoutingProvider`, `calculate_route()` |
| **Commute Intelligence & Policy Service** | `backend/app/services/commute_service.py` | `CommuteService`, `calculate_commute()`, `get_commute_matrix()` |
| **Deterministic Multi-Factor Ranking Engine** | `backend/app/services/ranking_service.py` | `RankingService`, `score_property()`, `calculate_final_score()`, `rank_properties()` |
| **Deterministic Property Comparison Engine** | `backend/app/services/comparison_service.py` | `ComparisonService`, `compare_properties()`, `calculate_dimension_winners()` |
| **AI Provider Protocol Base** | `backend/app/ai/base.py` | `AIProvider` (Protocol), `ParseSearchResponse`, `AIExplanationResponse` |
| **Local Ollama Inference Provider** | `backend/app/ai/ollama_provider.py` | `OllamaProvider`, `parse_intent()`, `explain_property()`, `health_check()` |
| **Google Gemini Cloud Inference Provider** | `backend/app/ai/gemini_provider.py` | `GeminiProvider`, `parse_intent()`, `explain_property()`, `health_check()` |
| **Deterministic Fallback AI Provider** | `backend/app/ai/fallback_provider.py` | `DeterministicFallbackProvider`, `parse_intent()`, `explain_property()` |
| **AI Provider Router & Deadline Manager** | `backend/app/ai/router.py` | `AIProviderRouter`, `execute_with_failover()`, `parse_conversational_search()` |
| **AI Query Complexity Scorer** | `backend/app/ai/routing_policy.py` | `evaluate_query_complexity()`, `should_use_cloud_model()` |
| **Ask the Map Conversational Orchestrator** | `backend/app/services/search_orchestrator.py` | `SearchOrchestrator`, `process_conversational_turn()`, `apply_patch()` |
| **Geographic Landmark & Hub Resolver** | `backend/app/utils/location_resolver.py` | `LocationResolver`, `resolve_destination()`, `get_city_bounds()` |
| **Price & Unit Parser** | `backend/app/utils/price_parser.py` | `parse_indian_currency()`, `normalize_price_range()` |
| **Alembic DB Migrations** | `backend/alembic/versions/` | `001_initial_schema.py`, `002_add_pois_table.py`, `003_add_reviews_and_ratings.py` |
| **Database Seeding Engine** | `backend/app/db/seed_all.py` | `seed_all()`, `seed_chennai_data()`, `seed_bengaluru_data()` |

---

## 2. Frontend Code Map

| Engineering Capability | File Path | Key Functions / Components |
| :--- | :--- | :--- |
| **Root Application Layout & Providers** | `frontend/app/layout.tsx` | `RootLayout`, mounts `Providers`, `Header`, `ComparisonBar`, `Footer` |
| **Global Context Providers** | `frontend/components/providers.tsx` | `Providers`, mounts `QueryClientProvider`, `FavoritesProvider`, `ComparisonProvider` |
| **Interactive Discovery & Search Page** | `frontend/app/search/page.tsx` | `SearchContent`, manages map/list sync, bbox search, ranking prefs, Ask the Map |
| **Property Detail Page** | `frontend/app/properties/[id]/page.tsx` | `PropertyDetailPage`, displays commute panel, location intelligence, AI explanation, modals |
| **Side-by-Side Comparison Page** | `frontend/app/compare/page.tsx` | `ComparePage`, displays comparison matrix, ranking deltas, AI summary |
| **Persistent Saved Properties Page** | `frontend/app/favorites/page.tsx` | `FavoritesPage`, renders saved grid with live counter and clear action |
| **MapLibre WebGL Container** | `frontend/components/map/map-container.tsx` | `MapContainer`, WebGL map instance, GeoJSON sources, markers, route line overlays |
| **Conversational Search Bar ("Ask the Map")** | `frontend/components/search/ask-the-map-bar.tsx` | `AskTheMapBar`, handles multi-turn queries, clarification pills, feedback chips |
| **Ranking Preferences Slider UI** | `frontend/components/search/ranking-preferences.tsx` | `RankingPreferences`, preset buttons, slider weights, travel mode selector |
| **Commute Calculation Panel** | `frontend/components/commute/commute-panel.tsx` | `CommutePanel`, travel mode tabs, destination selector, OSRM route trigger |
| **Location Intelligence POI Cards** | `frontend/components/properties/location-intelligence.tsx` | `LocationIntelligence`, categorical count badges, nearest distance meters |
| **Property Card & Ranked Card Components** | `frontend/components/properties/property-card.tsx`, `ranked-property-card.tsx` | `PropertyCard`, `RankedPropertyCard`, scoring breakdowns, compare/save buttons |
| **Persistent Comparison Context** | `frontend/context/comparison-context.tsx` | `ComparisonProvider`, `useComparison()`, `localStorage` key `estatemap_compare_properties` |
| **Persistent Favorites Context** | `frontend/context/favorites-context.tsx` | `FavoritesProvider`, `useFavorites()`, cross-tab sync, `estatemap_saved_properties` |
| **GeoJSON Converters & Serializers** | `frontend/lib/formatters/geojson.ts` | `propertyToFeature()`, `propertiesToFeatureCollection()`, `poiToFeature()` |
| **Backend API Client** | `frontend/lib/api/client.ts` | `apiClient`, `get()`, `post()`, `put()`, `del()`, error normalization |
