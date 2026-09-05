"use client";

import React, { Suspense, useState, useEffect } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { comparisonApi } from "@/lib/api/comparison";
import { PropertyComparisonRequest, ComparisonResult, AIComparisonResponse } from "@/types/comparison";
import { TravelMode, Property } from "@/types";
import { ComparisonTable } from "@/components/comparison/comparison-table";
import { RankingDiffCard } from "@/components/comparison/ranking-diff-card";
import { AIComparisonSummary } from "@/components/comparison/ai-comparison-summary";
import { MapContainer } from "@/components/map/map-container";
import { useComparison } from "@/context/comparison-context";
import {
  Scale,
  ArrowLeft,
  Navigation,
  Sparkles,
  MapPin,
  Car,
  Footprints,
  Bike,
  Bus,
  RefreshCw,
  SlidersHorizontal,
  Info,
  CheckCircle2,
} from "lucide-react";
import { getCityDestinations } from "@/lib/constants/destinations";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";

function CompareContent() {
  const searchParams = useSearchParams();
  const { selectedProperties } = useComparison();

  // Parse IDs from search params or comparison store
  const idsParam = searchParams?.get("ids");
  const parsedIds = idsParam
    ? idsParam
        .split(",")
        .map((id) => parseInt(id.trim(), 10))
        .filter((id) => !isNaN(id) && id > 0)
    : selectedProperties.map((p) => p.id);

  const uniqueIds = Array.from(new Set(parsedIds)).slice(0, 3);

  // Determine city from selected properties or query params
  const primaryProperty = selectedProperties.find((p) => uniqueIds.includes(p.id));
  const destinationPresets = React.useMemo(() => {
    const raw = getCityDestinations(
      primaryProperty?.city,
      primaryProperty?.latitude,
      primaryProperty?.longitude
    );
    return raw.map((d) => ({ name: d.name, lat: d.latitude, lng: d.longitude }));
  }, [primaryProperty?.city, primaryProperty?.latitude, primaryProperty?.longitude]);

  // Commute evaluation state
  const [selectedDest, setSelectedDest] = useState(destinationPresets[0]);
  const [travelMode, setTravelMode] = useState<TravelMode>(TravelMode.DRIVING);
  const [includeCommute, setIncludeCommute] = useState<boolean>(true);

  // Sync selected destination when presets change
  useEffect(() => {
    setSelectedDest((prev) => {
      const exists = destinationPresets.some((p) => p.name === prev.name);
      return exists ? prev : destinationPresets[0];
    });
  }, [destinationPresets]);

  // Request payload
  const comparisonRequest: PropertyComparisonRequest = {
    property_ids: uniqueIds,
    destination_lat: includeCommute ? selectedDest.lat : null,
    destination_lng: includeCommute ? selectedDest.lng : null,
    destination_name: includeCommute ? selectedDest.name : null,
    travel_mode: travelMode,
  };

  // 1. Deterministic comparison query
  const {
    data: comparisonData,
    isLoading: isCompareLoading,
    error: compareError,
    refetch: refetchComparison,
  } = useQuery<ComparisonResult>({
    queryKey: [
      "properties-compare",
      uniqueIds.join(","),
      includeCommute ? `${selectedDest.lat},${selectedDest.lng}` : "no-commute",
      travelMode,
    ],
    queryFn: () => comparisonApi.compareProperties(comparisonRequest),
    enabled: uniqueIds.length >= 2,
    staleTime: 60 * 1000,
  });

  // 2. Grounded AI explanation narrative query
  const {
    data: aiData,
    isLoading: isAiLoading,
    error: aiError,
    refetch: refetchAi,
  } = useQuery<AIComparisonResponse>({
    queryKey: [
      "ai-properties-compare",
      uniqueIds.join(","),
      includeCommute ? `${selectedDest.lat},${selectedDest.lng}` : "no-commute",
      travelMode,
    ],
    queryFn: () => comparisonApi.explainComparison(comparisonRequest),
    enabled: uniqueIds.length >= 2,
    staleTime: 120 * 1000,
  });

  if (uniqueIds.length < 2) {
    return (
      <div className="container mx-auto px-4 py-16 max-w-2xl text-center space-y-6">
        <div className="w-16 h-16 rounded-3xl bg-primary/10 text-primary mx-auto flex items-center justify-center shadow-inner">
          <Scale className="h-8 w-8" />
        </div>
        <div className="space-y-2">
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Select Properties to Compare
          </h1>
          <p className="text-sm text-muted-foreground max-w-md mx-auto">
            Choose 2 or 3 properties across the map or search results to generate a deterministic side-by-side comparison and AI trade-off narrative.
          </p>
        </div>
        <div className="flex items-center justify-center gap-3 pt-2">
          <Button asChild className="font-semibold shadow-md">
            <Link href="/search">
              <span>Search Properties</span>
            </Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/">
              <ArrowLeft className="mr-1.5 h-4 w-4" />
              <span>Back to Home</span>
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  // Convert facts to Property entities for MapContainer preview
  const mapProperties: Property[] = comparisonData
    ? comparisonData.properties.map((p) => ({
        id: p.id,
        owner_id: 1,
        title: `${p.label}: ${p.title}`,
        price: p.price,
        property_type: p.property_type,
        bedrooms: p.bedrooms || 0,
        bathrooms: p.bathrooms || 0,
        area_sqft: p.area_sqft || 0,
        address: p.address,
        locality: p.locality,
        city: p.city,
        latitude: p.latitude,
        longitude: p.longitude,
        status: "active",
        images: p.image_urls.map((url, i) => ({
          id: i + 1,
          property_id: p.id,
          image_url: url,
          display_order: i,
          is_primary: i === 0,
          created_at: new Date().toISOString(),
        })),
        amenities: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }))
    : [];

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl space-y-8">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-border pb-6">
        <div>
          <div className="flex items-center gap-2 mb-1.5">
            <Button asChild variant="ghost" size="sm" className="h-7 px-2 text-xs text-muted-foreground">
              <Link href="/search">
                <ArrowLeft className="mr-1 h-3.5 w-3.5" />
                Back to Search
              </Link>
            </Button>
            <Badge variant="secondary" className="text-xs font-semibold px-2 py-0.5">
              Comparing {uniqueIds.length} Properties
            </Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-foreground flex items-center gap-2.5">
            Property Comparison & Trade-off Analysis
          </h1>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              refetchComparison();
              refetchAi();
            }}
            className="text-xs font-medium gap-1.5"
            disabled={isCompareLoading || isAiLoading}
          >
            <RefreshCw className={`h-3.5 w-3.5 ${isCompareLoading || isAiLoading ? "animate-spin" : ""}`} />
            Refresh Comparison
          </Button>
        </div>
      </div>

      {/* Commute Evaluation Bar */}
      <div className="rounded-2xl border border-border bg-card p-4 sm:p-5 shadow-xs space-y-3">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-primary/10 text-primary">
              <Navigation className="h-4 w-4" />
            </div>
            <div>
              <h3 className="text-sm font-semibold text-foreground">Commute Destination Evaluator</h3>
              <p className="text-xs text-muted-foreground">
                Compare actual road-network travel duration from each property
              </p>
            </div>
          </div>

          {/* Travel Mode Toggle */}
          <div className="flex items-center gap-1 bg-muted/60 p-1 rounded-xl">
            <button
              onClick={() => setTravelMode(TravelMode.DRIVING)}
              className={`p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all ${
                travelMode === TravelMode.DRIVING ? "bg-background text-foreground shadow-xs font-semibold" : "text-muted-foreground hover:text-foreground"
              }`}
              title="Driving"
            >
              <Car className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Drive</span>
            </button>
            <button
              onClick={() => setTravelMode(TravelMode.TRANSIT)}
              className={`p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all ${
                travelMode === TravelMode.TRANSIT ? "bg-background text-foreground shadow-xs font-semibold" : "text-muted-foreground hover:text-foreground"
              }`}
              title="Transit"
            >
              <Bus className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Transit</span>
            </button>
            <button
              onClick={() => setTravelMode(TravelMode.BICYCLING)}
              className={`p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all ${
                travelMode === TravelMode.BICYCLING ? "bg-background text-foreground shadow-xs font-semibold" : "text-muted-foreground hover:text-foreground"
              }`}
              title="Bicycling"
            >
              <Bike className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Cycle</span>
            </button>
            <button
              onClick={() => setTravelMode(TravelMode.WALKING)}
              className={`p-1.5 rounded-lg text-xs flex items-center gap-1 transition-all ${
                travelMode === TravelMode.WALKING ? "bg-background text-foreground shadow-xs font-semibold" : "text-muted-foreground hover:text-foreground"
              }`}
              title="Walking"
            >
              <Footprints className="h-3.5 w-3.5" />
              <span className="hidden sm:inline">Walk</span>
            </button>
          </div>
        </div>

        {/* Destination Presets */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          <span className="text-muted-foreground font-medium shrink-0 flex items-center gap-1">
            <MapPin className="h-3 w-3 text-primary" />
            Preset Destination:
          </span>
          {destinationPresets.map((dest) => (
            <button
              key={dest.name}
              onClick={() => setSelectedDest(dest)}
              className={`px-3 py-1.5 rounded-xl border text-xs font-medium transition-all shrink-0 ${
                selectedDest.name === dest.name
                  ? "border-primary bg-primary/10 text-primary font-semibold shadow-xs"
                  : "border-border/70 bg-background text-muted-foreground hover:border-primary/40 hover:text-foreground"
              }`}
            >
              {dest.name}
            </button>
          ))}
        </div>
      </div>

      {/* Grounded AI Comparative Narrative */}
      <AIComparisonSummary
        data={aiData}
        isLoading={isAiLoading}
        error={aiError ? "Failed to load AI comparison" : null}
      />

      {/* Deterministic Summary Statements (Fast fallback / Facts Strip) */}
      {comparisonData && comparisonData.deterministic_summary.length > 0 && (
        <div className="rounded-2xl border border-border/80 bg-muted/20 p-4 sm:p-5 space-y-2.5">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
            <Info className="h-3.5 w-3.5 text-primary" />
            Deterministic Key Differentiators
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {comparisonData.deterministic_summary.map((stmt, idx) => (
              <div
                key={idx}
                className="flex items-start gap-2 bg-background/80 border border-border/50 rounded-xl p-2.5 text-xs text-foreground/90 font-medium"
              >
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 mt-0.5 shrink-0" />
                <span>{stmt}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Main Comparison Table */}
      {comparisonData ? (
        <ComparisonTable comparison={comparisonData} />
      ) : isCompareLoading ? (
        <div className="rounded-2xl border border-border bg-card p-12 text-center space-y-4 animate-pulse">
          <div className="w-10 h-10 rounded-full bg-primary/20 mx-auto" />
          <div className="h-4 w-48 bg-muted mx-auto rounded" />
          <div className="h-3 w-64 bg-muted/60 mx-auto rounded" />
        </div>
      ) : compareError ? (
        <div className="rounded-2xl border border-destructive/30 bg-destructive/5 p-8 text-center text-destructive text-sm font-medium">
          Failed to compute multi-property comparison. Please ensure valid property selections.
        </div>
      ) : null}

      {/* "Why This Ranked Higher" Factor Contribution Breakdowns */}
      {comparisonData && comparisonData.ranking_deltas.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-emerald-500/10 text-emerald-600">
              <Sparkles className="h-3.5 w-3.5" />
            </div>
            <h3 className="text-base font-semibold text-foreground">
              Mathematical Ranking Advantage & Contribution Analysis
            </h3>
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {comparisonData.ranking_deltas.map((delta, idx) => (
              <RankingDiffCard key={idx} delta={delta} />
            ))}
          </div>
        </div>
      )}

      {/* Interactive Map Preview with Markers A, B, C */}
      {mapProperties.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className="flex h-6 w-6 items-center justify-center rounded-lg bg-primary/10 text-primary">
                <MapPin className="h-3.5 w-3.5" />
              </div>
              <h3 className="text-base font-semibold text-foreground">Geographic Distribution</h3>
            </div>
            <span className="text-xs text-muted-foreground">
              MapLibre PostGIS spatial synchronization
            </span>
          </div>

          <div className="h-[380px] w-full rounded-2xl overflow-hidden border border-border shadow-xs">
            <MapContainer
              properties={mapProperties}
              latitude={mapProperties[0]?.latitude || 12.9716}
              longitude={mapProperties[0]?.longitude || 77.5946}
              zoom={11}
            />
          </div>
        </div>
      )}
    </div>
  );
}

export default function ComparePage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto px-4 py-16 text-center space-y-4 animate-pulse">
          <div className="w-12 h-12 rounded-2xl bg-primary/10 mx-auto" />
          <div className="h-4 w-36 bg-muted mx-auto rounded" />
        </div>
      }
    >
      <CompareContent />
    </Suspense>
  );
}
