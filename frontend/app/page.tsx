"use client";

import React, { useEffect, useState } from "react";
import Link from "next/link";
import {
  ArrowRight,
  Compass,
  Database,
  Layers,
  MapPin,
  ShieldCheck,
  Sparkles,
} from "lucide-react";
import { listProperties } from "@/lib/api/properties";
import { Property } from "@/types";
import { PropertyGrid } from "@/components/properties/property-grid";
import { SearchBar } from "@/components/search/search-bar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";

// Demo sample listings for visual richness when DB has no items yet
const DEMO_FEATURED_PROPERTIES: Property[] = [
  {
    id: 101,
    owner_id: 1,
    title: "Luxury 3BHK Penthouse in Whitefield",
    description: "Panoramic city skyline views with premium amenities.",
    price: 18500000,
    property_type: "apartment",
    bedrooms: 3,
    bathrooms: 3,
    area_sqft: 2400,
    address: "ITPB Main Road, Whitefield",
    city: "Bengaluru",
    locality: "Whitefield",
    latitude: 12.9698,
    longitude: 77.7499,
    status: "active",
    images: [],
    amenities: [
      { id: 1, name: "Swimming Pool", category: "Leisure" },
      { id: 2, name: "Gymnasium", category: "Fitness" },
      { id: 3, name: "24/7 Security", category: "Safety" },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: 102,
    owner_id: 1,
    title: "Contemporary 4BHK Villa near Outer Ring Road",
    description: "Private garden, solar power backup, and gated security.",
    price: 32000000,
    property_type: "villa",
    bedrooms: 4,
    bathrooms: 4,
    area_sqft: 3800,
    address: "Sarjapur-Marathahalli Ring Road",
    city: "Bengaluru",
    locality: "Sarjapur",
    latitude: 12.9249,
    longitude: 77.6835,
    status: "active",
    images: [],
    amenities: [
      { id: 2, name: "Gymnasium", category: "Fitness" },
      { id: 4, name: "Private Garden", category: "Outdoor" },
      { id: 5, name: "Power Backup", category: "Utility" },
    ],
    created_at: new Date().toISOString(),
  },
  {
    id: 103,
    owner_id: 1,
    title: "Modern 2BHK Apartment in Indiranagar",
    description: "Walkable to metro station and 100 Feet Road restaurants.",
    price: 14500000,
    property_type: "apartment",
    bedrooms: 2,
    bathrooms: 2,
    area_sqft: 1350,
    address: "100 Feet Road, Indiranagar",
    city: "Bengaluru",
    locality: "Indiranagar",
    latitude: 12.9719,
    longitude: 77.6412,
    status: "active",
    images: [],
    amenities: [
      { id: 1, name: "Swimming Pool", category: "Leisure" },
      { id: 3, name: "24/7 Security", category: "Safety" },
    ],
    created_at: new Date().toISOString(),
  },
];

const POPULAR_LOCALITIES = [
  { name: "Indiranagar", city: "Bengaluru", count: "128 listings", avg: "₹1.4 Cr avg" },
  { name: "Whitefield", city: "Bengaluru", count: "340 listings", avg: "₹95 L avg" },
  { name: "Koramangala", city: "Bengaluru", count: "95 listings", avg: "₹1.6 Cr avg" },
  { name: "HSR Layout", city: "Bengaluru", count: "215 listings", avg: "₹1.2 Cr avg" },
  { name: "Bandra West", city: "Mumbai", count: "84 listings", avg: "₹4.8 Cr avg" },
  { name: "Gachibowli", city: "Hyderabad", count: "192 listings", avg: "₹1.1 Cr avg" },
];

export default function HomePage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    listProperties({ page_size: 6, sort_by: "newest" })
      .then((res) => {
        if (res.items && res.items.length > 0) {
          setProperties(res.items);
        } else {
          setProperties(DEMO_FEATURED_PROPERTIES);
        }
      })
      .catch(() => {
        setProperties(DEMO_FEATURED_PROPERTIES);
      })
      .finally(() => setIsLoading(false));
  }, []);

  return (
    <div className="flex flex-col">
      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border bg-gradient-to-b from-card via-background to-background py-16 sm:py-24">
        {/* Subtle grid background */}
        <div
          className="absolute inset-0 opacity-[0.03] dark:opacity-[0.05]"
          style={{
            backgroundImage: "radial-gradient(#0284c7 1px, transparent 1px)",
            backgroundSize: "24px 24px",
          }}
        />

        <div className="relative mx-auto max-w-5xl px-4 text-center sm:px-6 lg:px-8">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 rounded-full border border-border bg-card px-3.5 py-1 text-xs font-medium text-muted-foreground shadow-sm">
            <MapPin className="h-3.5 w-3.5 text-primary" />
            <span>Location-First Real Estate Discovery</span>
          </div>

          {/* Headline */}
          <h1 className="mt-6 text-3xl font-extrabold tracking-tight sm:text-5xl text-foreground max-w-3xl mx-auto leading-tight">
            Find a place that fits your life, verified by location intelligence.
          </h1>

          <p className="mt-4 text-base text-muted-foreground sm:text-lg max-w-2xl mx-auto">
            Discover verified homes with PostGIS spatial precision, commute insights,
            and interactive vector maps.
          </p>

          {/* Hero Search Bar */}
          <div className="mt-8 max-w-2xl mx-auto">
            <SearchBar size="lg" placeholder="Search by locality, city, or landmark (e.g. Indiranagar, Whitefield)..." />
          </div>

          {/* Quick Filter City Pills */}
          <div className="mt-4 flex flex-wrap items-center justify-center gap-2 text-xs text-muted-foreground">
            <span className="font-medium text-foreground/70">Popular Cities:</span>
            {["Bengaluru", "Mumbai", "Chennai", "Hyderabad", "Delhi NCR", "Pune"].map(
              (city) => (
                <Link
                  key={city}
                  href={`/search?city=${encodeURIComponent(city)}`}
                  className="rounded-full border border-border bg-card px-3 py-1 font-medium text-muted-foreground transition-colors hover:border-primary hover:text-primary"
                >
                  {city}
                </Link>
              )
            )}
          </div>
        </div>
      </section>

      {/* Popular Micro-Markets */}
      <section className="mx-auto w-full max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold tracking-tight text-foreground">
              Popular Micro-Markets
            </h2>
            <p className="text-xs text-muted-foreground mt-0.5">
              High-demand residential hubs with verified transit and amenities
            </p>
          </div>
          <Link
            href="/search"
            className="flex items-center gap-1 text-xs font-semibold text-primary hover:underline"
          >
            <span>View all on map</span>
            <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {POPULAR_LOCALITIES.map((loc) => (
            <Link
              key={loc.name}
              href={`/search?locality=${encodeURIComponent(loc.name)}`}
              className="group flex flex-col justify-between rounded-lg border border-border bg-card p-3.5 shadow-sm transition-all hover:border-primary/40 hover:shadow-md"
            >
              <div>
                <div className="font-semibold text-sm text-foreground group-hover:text-primary transition-colors">
                  {loc.name}
                </div>
                <div className="text-[11px] text-muted-foreground">{loc.city}</div>
              </div>
              <div className="mt-3 flex items-center justify-between border-t border-border/60 pt-2 text-[11px]">
                <span className="text-muted-foreground">{loc.count}</span>
                <span className="font-medium text-foreground/80">{loc.avg}</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Featured Properties */}
      <section className="border-t border-border bg-muted/20 py-12">
        <div className="mx-auto w-full max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold tracking-tight text-foreground">
                Featured Properties
              </h2>
              <p className="text-xs text-muted-foreground mt-0.5">
                Handpicked residential listings with verified spatial coordinates
              </p>
            </div>
            <Link href="/search">
              <Button variant="outline" size="sm" className="h-8 gap-1 text-xs">
                <span>Browse all</span>
                <ArrowRight className="h-3.5 w-3.5" />
              </Button>
            </Link>
          </div>

          <div className="mt-6">
            <PropertyGrid
              properties={properties}
              isLoading={isLoading}
              columns={3}
            />
          </div>
        </div>
      </section>

      {/* Platform Architecture Pillars */}
      <section className="mx-auto w-full max-w-7xl px-4 py-16 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto">
          <Badge variant="secondary" className="text-xs font-semibold">
            Engineering Excellence
          </Badge>
          <h2 className="mt-3 text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
            Location is the Product, Not an Afterthought
          </h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Conventional portals show static listings with disconnected maps. EstateMap
            AI is built from the ground up around spatial indexing and location intelligence.
          </p>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-3">
          <div className="flex flex-col rounded-lg border border-border bg-card p-6 shadow-sm">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Database className="h-5 w-5" />
            </div>
            <h3 className="mt-4 font-semibold text-base text-foreground">
              PostGIS Spatial Indexing
            </h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Every listing is stored as a true WGS84 geographic point with GiST spatial
              indexes, powering sub-millisecond bounding box and radius queries.
            </p>
          </div>

          <div className="flex flex-col rounded-lg border border-border bg-card p-6 shadow-sm">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
              <Layers className="h-5 w-5" />
            </div>
            <h3 className="mt-4 font-semibold text-base text-foreground">
              mapcn & MapLibre GL
            </h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Composable vector maps with GPU-accelerated rendering, synchronized card/marker
              highlighting, and boundary draw search.
            </p>
          </div>

          <div className="flex flex-col rounded-lg border border-border bg-card p-6 shadow-sm">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-50 text-sky-700 dark:bg-sky-950 dark:text-sky-300">
              <ShieldCheck className="h-5 w-5" />
            </div>
            <h3 className="mt-4 font-semibold text-base text-foreground">
              Deterministic Scoring
            </h3>
            <p className="mt-2 text-xs text-muted-foreground leading-relaxed">
              Transparent multi-factor ranking based on commute distance, price per sq ft,
              and amenity availability with factual AI explanations.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}

