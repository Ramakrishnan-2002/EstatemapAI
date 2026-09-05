# EstateMap AI — Frontend Architecture & Design System

## 1. Executive Summary

EstateMap AI's frontend is a commercial-grade, location-first real estate discovery interface built with **Next.js 14 (App Router)**, **TypeScript**, **Tailwind CSS**, and **TanStack Query (React Query)**.

The frontend is engineered with an aesthetic visual language of **Trust, Precision, Location, Property, Clarity, and Professionalism** — avoiding generic SaaS clichés or AI novelty tropes in favor of an institutional real estate portal experience (such as StreetEasy, Rightmove, or Redfin).

---

## 2. Technology Stack & Key Architectural Choices

| Category | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | Next.js 14 (App Router) | Server/Client Component model, fast route transitions, SEO-optimized metadata. |
| **Language** | TypeScript (Strict Mode) | End-to-end type safety mapped directly to backend FastAPI Pydantic schemas. |
| **Styling** | Tailwind CSS + CSS Variables | Scalable design token system with support for dark/light themes. |
| **State & Fetching** | TanStack Query v5 | Server state caching, optimistic updates, request deduplication, and background refetching. |
| **Icons** | Lucide React | Lightweight, tree-shakable SVG icon set. |
| **Map Boundary** | `MapContainer` | Modular container boundary designed for clean drop-in integration with `mapcn` & MapLibre GL in Phase 5. |

---

## 3. Directory Structure

```text
frontend/
├── app/
│   ├── layout.tsx                 # Root layout with Header, Footer, TanStack Query Providers
│   ├── globals.css                # Custom CSS variables, theme tokens, and typography
│   ├── page.tsx                   # Homepage (Hero search, micro-markets, featured grid, platform pillars)
│   ├── search/
│   │   └── page.tsx               # Split-view search (Filter bar, property list, map container boundary)
│   ├── properties/
│   │   └── [id]/
│   │       └── page.tsx           # Property detail view (Gallery, specs, amenities, location context)
│   ├── login/
│   │   └── page.tsx               # User authentication login
│   ├── register/
│   │   └── page.tsx               # Account registration
│   ├── favorites/
│   │   └── page.tsx               # Saved properties and collections
│   └── dashboard/
│       └── page.tsx               # User profile, active listings, search alerts
├── components/
│   ├── ui/                        # Low-level UI primitives
│   │   ├── button.tsx             # Button (default, secondary, outline, ghost, destructive, emerald)
│   │   ├── input.tsx              # Form input with label, error feedback, and helper text
│   │   ├── badge.tsx              # Status & category badges (default, secondary, outline, success, warning, etc.)
│   │   ├── card.tsx               # Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter
│   │   ├── skeleton.tsx           # Shimmer loading skeleton
│   │   └── select.tsx             # Form select dropdown with standardized styling
│   ├── layout/                    # Application shell
│   │   ├── header.tsx             # Responsive header with branding, navigation links, and auth states
│   │   ├── footer.tsx             # Platform footer with legal links, city directories, and newsletter
│   │   └── shell.tsx              # Container wrapper with max-width and padding constraints
│   ├── feedback/                  # Standardized feedback states
│   │   └── states.tsx             # LoadingState, EmptyState, ErrorState
│   ├── properties/                # Domain-specific property components
│   │   ├── price-display.tsx      # Formatted price (INR Cr/L/K) + Price per sq ft
│   │   ├── location-display.tsx   # Locality, city, pin code with map pin icon
│   │   ├── property-meta.tsx      # Beds, baths, built-up area, property type badges
│   │   ├── amenity-list.tsx       # Grid/list of categorized amenities with category badges
│   │   ├── property-card.tsx      # Listing card with image, price, tags, and favorite toggle
│   │   ├── property-card-skeleton.tsx # Shimmer placeholder for property cards
│   │   └── property-grid.tsx      # Responsive grid with built-in empty, error, and loading states
│   ├── search/                    # Search & filtering controls
│   │   ├── search-bar.tsx         # Hero and split-view search input with debounce & geolocation trigger
│   │   └── filter-bar.tsx         # Filters for price range, BHK count, property type, and sorting
│   ├── map/                       # Map integration boundary
│   │   └── map-container.tsx      # MapLibre/mapcn host boundary with coordinate badge, viewport controls
│   └── providers.tsx              # TanStack React Query Client Provider
├── lib/
│   ├── api/
│   │   ├── client.ts              # Unified fetch wrapper with auth token handling & backend error parsing
│   │   ├── auth.ts                # Auth API methods: login, register, getMe, logout
│   │   └── properties.ts          # Property API methods: listProperties, getPropertyById, create, update, delete
│   └── formatters/
│       ├── currency.ts            # Indian Rupee (INR) formatting (Cr, L, K) + price per sq ft
│       ├── property.ts            # Bedroom, bathroom, area (sq ft), and type formatters
│       └── date.ts                # Date and relative time formatters
├── types/
│   └── index.ts                   # Canonical TypeScript interfaces matching FastAPI schemas
├── __tests__/
│   ├── formatters.test.ts         # Unit tests for currency, property, and date formatters
│   └── api-client.test.ts         # Unit tests for API client error handling and token injection
├── tailwind.config.ts             # Tailwind CSS configuration with design system tokens
├── tsconfig.json                  # Strict TypeScript configuration
├── package.json                   # Project dependencies and test scripts
└── .eslintrc.json                 # ESLint Next.js configuration
```

---

## 4. Design System & Tokens

### 4.1 Color Palette
The color system emphasizes precision, trustworthiness, and high contrast:
- **Primary / Brand Slate (`#0f172a` - `#1e293b`)**: Foundation for navigation, deep backgrounds, and typography.
- **Accent Emerald (`#059669` / `#10b981`)**: Used for primary action buttons, verified badges, active states, and positive signals.
- **Muted Grays (`#64748b` - `#f1f5f9`)**: Used for secondary text, borders, dividers, and background surfaces.
- **Alert Colors**: Red (`#ef4444`) for errors/destructive actions, Amber (`#f59e0b`) for pending/warnings.

### 4.2 Typography & Spacing
- Standardized typography scale (`text-xs` to `text-4xl`) paired with crisp sans-serif fonts (`Inter`, `system-ui`).
- Consistent 4px grid rhythm (`gap-2`, `gap-4`, `gap-6`, `gap-8`).

---

## 5. Canonical Type Safety Layer

All frontend types in `types/index.ts` strictly match the FastAPI backend's Pydantic schemas:

```typescript
export interface Property {
  id: string;
  title: string;
  description?: string | null;
  property_type: PropertyType;
  listing_type: ListingType;
  status: PropertyStatus;
  price: number;
  currency: string;
  price_per_sqft?: number | null;
  bedrooms?: number | null;
  bathrooms?: number | null;
  balconies?: number | null;
  carpet_area_sqft?: number | null;
  built_up_area_sqft?: number | null;
  furnishing_status?: FurnishingStatus | null;
  facing_direction?: FacingDirection | null;
  floor_number?: number | null;
  total_floors?: number | null;
  locality: string;
  city: string;
  state: string;
  country: string;
  pin_code?: string | null;
  latitude: number;
  longitude: number;
  owner_id?: string | null;
  created_at: string;
  updated_at: string;
  images: PropertyImage[];
  amenities: Amenity[];
}
```

---

## 6. Unified API Client & Error Handling

The API client (`lib/api/client.ts`) centralizes HTTP communication and automatically unwraps backend error envelopes:

```typescript
// Backend Error Envelope:
// { "error": { "code": "NOT_FOUND", "message": "Property not found", "details": {}, "request_id": "req-123" } }

export async function apiClient<T>(endpoint: string, options?: RequestInit): Promise<T> {
  // 1. Injects Bearer auth token if present in localStorage / memory
  // 2. Automatically sets Content-Type: application/json
  // 3. Normalizes backend error format into throw new APIError(...)
}
```

---

## 7. MapLibre / mapcn Integration Boundary

To prepare for Phase 5 without introducing half-implemented or competing map libraries, `frontend/components/map/map-container.tsx` defines the strict component boundary:

- Marked with `data-testid="mapcn-container-boundary"`.
- Displays real-time coordinate readouts, zoom controls, and mock property pin overlays.
- Seamlessly switches between full map and split-view modes on desktop and mobile.
- Ready to be swapped with `<MapLibreGL>` / `<MapcnView>` in Phase 5 without restructuring pages or layouts.
