# EstateMap AI — Development Guide

## 1. Prerequisites
- **Docker & Docker Compose** (Docker Desktop or Docker Engine v24+)
- **Python 3.12+** (for local backend development)
- **Node.js 20+ & npm** (for local frontend development)
- **Ollama** (optional, for local `llama3.2:3b` testing)

---

## 2. Quickstart with Docker Compose

### 1. Configure Environment
```bash
cp .env.example .env
```

### 2. Start PostgreSQL/PostGIS and Redis Services
```bash
docker compose up -d postgres-postgis redis
```

### 3. Run Database Migrations (Alembic)
```bash
docker compose run --rm backend alembic upgrade head
```

### 4. Start Full Development Stack
```bash
docker compose up --build
```
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **Swagger Interactive API Docs**: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- **Health Diagnostic**: [http://localhost:8000/health](http://localhost:8000/health)
- **Liveness Probe**: [http://localhost:8000/health/live](http://localhost:8000/health/live)
- **Readiness Probe**: [http://localhost:8000/health/ready](http://localhost:8000/health/ready)
- **Frontend Web Application**: [http://localhost:3000](http://localhost:3000)

---

## 3. Testing & Code Quality Checks

### Run All Backend Tests (Docker)
```bash
docker compose run --rm backend pytest -v
```

### Run Unit Tests Only
```bash
docker compose run --rm backend pytest tests/unit -v
```

### Run Integration Tests Only (PostGIS, Redis, Auth)
```bash
docker compose run --rm backend pytest tests/integration -v
```

### Run Linter & Formatter Checks
```bash
docker compose run --rm backend ruff check .
docker compose run --rm backend ruff format --check .
```

### Auto-fix Linting & Formatting
```bash
docker compose run --rm backend ruff check --fix .
docker compose run --rm backend ruff format .
```

---

## 4. Alembic Database Migration Commands

### Create a New Migration
```bash
docker compose run --rm backend alembic revision -m "description_of_change"
```

### Apply Migrations to Head
```bash
docker compose run --rm backend alembic upgrade head
```

### Rollback Last Migration
```bash
docker compose run --rm backend alembic downgrade -1
```

### Rollback All Migrations
```bash
docker compose run --rm backend alembic downgrade base
```

---

## 5. API Authentication Quick Guide

### Register a User
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"MyPassword123!","full_name":"Test User"}'
```

### Login & Get JWT Access Token
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"MyPassword123!"}'
```

### Access Protected Profile Endpoint (`/users/me`)
```bash
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer <access_token>"
```

---

## 6. Property Management Quick Guide

### Create a Property Listing
```bash
curl -X POST http://localhost:8000/api/v1/properties \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Modern 3BHK Apartment in Indiranagar",
    "description": "Spacious sun-lit apartment close to metro station.",
    "price": 14500000.0,
    "property_type": "apartment",
    "bedrooms": 3,
    "bathrooms": 2.0,
    "area_sqft": 1650.0,
    "address": "100 Feet Road, Indiranagar",
    "city": "Bengaluru",
    "locality": "Indiranagar",
    "latitude": 12.9719,
    "longitude": 77.6412,
    "image_urls": ["https://cdn.estatemap.ai/img1.jpg"],
    "amenity_ids": []
  }'
```

### List Properties with Filtering and Pagination
```bash
curl -X GET "http://localhost:8000/api/v1/properties?city=Bengaluru&min_price=5000000&sort_by=price_asc&page=1&page_size=10"
```

### Get Property by ID
```bash
curl -X GET http://localhost:8000/api/v1/properties/1
```

### Update Property (Owner Only)
```bash
curl -X PATCH http://localhost:8000/api/v1/properties/1 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"price": 14000000.0, "status": "active"}'
```

### Delete Property (Owner Only)
```bash
curl -X DELETE http://localhost:8000/api/v1/properties/1 \
  -H "Authorization: Bearer <access_token>"
```

---

## 7. Frontend Development & Code Quality Checks

### Run Type Checking
```bash
docker compose run --rm frontend npm run type-check
```

### Run ESLint Checks
```bash
docker compose run --rm frontend npm run lint
```

### Build Production Bundle
```bash
docker compose run --rm frontend npm run build
```


