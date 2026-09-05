# EstateMap AI — Database Design & Spatial Indexing

## 1. Relational & Spatial Entity-Relationship Model

### `users` Table
- `id` (SERIAL PRIMARY KEY)
- `email` (VARCHAR UNIQUE NOT NULL, Indexed)
- `hashed_password` (VARCHAR NOT NULL)
- `full_name` (VARCHAR)
- `is_active` (BOOLEAN DEFAULT TRUE)
- `is_superuser` (BOOLEAN DEFAULT FALSE)
- `created_at` (TIMESTAMPTZ DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ)

### `properties` Table
- `id` (SERIAL PRIMARY KEY)
- `owner_id` (INTEGER REFERENCES users(id) ON DELETE CASCADE, Indexed)
- `title` (VARCHAR NOT NULL)
- `description` (TEXT)
- `price` (NUMERIC(14, 2) NOT NULL, Indexed)
- `property_type` (VARCHAR(50) NOT NULL, Indexed)
- `bedrooms` (SMALLINT NOT NULL, Indexed)
- `bathrooms` (SMALLINT NOT NULL)
- `area_sqft` (NUMERIC(10, 2) NOT NULL)
- `address` (VARCHAR NOT NULL)
- `city` (VARCHAR(100) NOT NULL, Indexed)
- `locality` (VARCHAR(100) NOT NULL, Indexed)
- `location` (`GEOMETRY(Point, 4326)` NOT NULL) -> **Indexed with GiST Index**
- `status` (VARCHAR(30) DEFAULT 'available', Indexed)
- `created_at` (TIMESTAMPTZ DEFAULT NOW(), Indexed)
- `updated_at` (TIMESTAMPTZ)

### `amenities` Table
- `id` (SERIAL PRIMARY KEY)
- `name` (VARCHAR(100) UNIQUE NOT NULL)
- `category` (VARCHAR(50) NOT NULL)
- `icon` (VARCHAR(50))

### `property_amenities` (Junction Table)
- `property_id` (INTEGER REFERENCES properties(id) ON DELETE CASCADE)
- `amenity_id` (INTEGER REFERENCES amenities(id) ON DELETE CASCADE)
- PRIMARY KEY (`property_id`, `amenity_id`)

### `property_images` Table
- `id` (SERIAL PRIMARY KEY)
- `property_id` (INTEGER REFERENCES properties(id) ON DELETE CASCADE, Indexed)
- `image_url` (VARCHAR NOT NULL)
- `is_primary` (BOOLEAN DEFAULT FALSE)
- `display_order` (SMALLINT DEFAULT 0)

### `favorites` Table
- `id` (SERIAL PRIMARY KEY)
- `user_id` (INTEGER REFERENCES users(id) ON DELETE CASCADE)
- `property_id` (INTEGER REFERENCES properties(id) ON DELETE CASCADE)
- `created_at` (TIMESTAMPTZ DEFAULT NOW())
- UNIQUE (`user_id`, `property_id`)

### `property_views` Table
- `id` (BIGSERIAL PRIMARY KEY)
- `property_id` (INTEGER REFERENCES properties(id) ON DELETE CASCADE)
- `user_id` (INTEGER REFERENCES users(id) ON DELETE SET NULL)
- `viewed_at` (TIMESTAMPTZ DEFAULT NOW())

### `pois` Table (Points of Interest - Phase 7)
- `id` (SERIAL PRIMARY KEY)
- `name` (VARCHAR(255) NOT NULL, Indexed)
- `category` (VARCHAR(50) NOT NULL, Indexed, CHECK IN ('hospital', 'school', 'transit', 'supermarket', 'park', 'pharmacy', 'bank'))
- `subcategory` (VARCHAR(100))
- `location` (`GEOMETRY(Point, 4326)` NOT NULL) -> **Indexed with GiST Index `idx_pois_location_gist`**
- `address` (VARCHAR(500))
- `city` (VARCHAR(100) NOT NULL, Indexed)
- `locality` (VARCHAR(100), Indexed)
- `is_active` (BOOLEAN DEFAULT TRUE NOT NULL, Indexed)
- `created_at` (TIMESTAMPTZ DEFAULT NOW())
- `updated_at` (TIMESTAMPTZ)
- Composite Index: `ix_pois_category_active` on `(category, is_active)`

---

## 2. Spatial Indexing & Query Patterns
- **GiST Spatial Index on Properties & POIs**:
  ```sql
  CREATE INDEX idx_properties_location_gist ON properties USING GIST (location);
  CREATE INDEX idx_pois_location_gist ON pois USING GIST (location);
  CREATE INDEX ix_pois_category_active ON pois (category, is_active);
  ```
- **Bounding Box Query (POIs & Properties)**:
  ```sql
  SELECT id, name, category, ST_AsGeoJSON(location)::json AS geometry
  FROM pois
  WHERE is_active = true
    AND ST_Within(location, ST_MakeEnvelope(:west, :south, :east, :north, 4326));
  ```
- **Radius Search (ST_DWithin on Geography)**:
  ```sql
  SELECT id, name, category,
         ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0 AS distance_km
  FROM pois
  WHERE is_active = true
    AND ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_meters)
  ORDER BY distance_km ASC;
  ```
- **Nearest POI by Category**:
  ```sql
  SELECT id, name, category,
         ST_Distance(location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0 AS distance_km
  FROM pois
  WHERE is_active = true AND category = :category
  ORDER BY distance_km ASC
  LIMIT 1;
  ```
- **POI Count within Radius**:
  ```sql
  SELECT COUNT(*)
  FROM pois
  WHERE is_active = true AND category = :category
    AND ST_DWithin(location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_meters);
  ```

