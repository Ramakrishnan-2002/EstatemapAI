"use client";

import React, { Suspense, useCallback, useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { ChevronLeft, ChevronRight, List, Map as MapIcon, Sparkles, SlidersHorizontal, MessageSquare } from "lucide-react";
import { searchPropertiesByBBox } from "@/lib/api/geo";
import { getMapPOIs } from "@/lib/api/pois";
import { listProperties } from "@/lib/api/properties";
import { searchRankedProperties } from "@/lib/api/ranking";
import {
  MapBounds,
  MapViewportState,
  POICategory,
  POIGeoJSONFeature,
  Property,
  PropertyFilterParams,
  RankedPropertyItem,
} from "@/types";
import {
  ConversationalSearchState,
  AskMapResponse,
} from "@/types/conversational_search";
import { ErrorState, LoadingState } from "@/components/feedback/states";
import { MapContainer } from "@/components/map/map-container";
import { POIFilter } from "@/components/map/poi-filter";
import { PropertyGrid } from "@/components/properties/property-grid";
import { FilterBar } from "@/components/search/filter-bar";
import { SearchBar } from "@/components/search/search-bar";
import {
  RankingPreferences,
  RankingPreferencesState,
  WEIGHT_PRESETS,
} from "@/components/search/ranking-preferences";
import { NaturalLanguageSearch } from "@/components/search/natural-language-search";
import { AskTheMapBar } from "@/components/search/ask-the-map-bar";
import { PropertySearchIntent } from "@/types/ai";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { useFavorites } from "@/context/favorites-context";

function SearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { savedIds, toggleSave } = useFavorites();

  // Initialize filters from URL query parameters
  const [filters, setFilters] = useState<PropertyFilterParams>({
    city: searchParams.get("city") || undefined,
    locality: searchParams.get("locality") || undefined,
    property_type: searchParams.get("property_type") || undefined,
    min_price: searchParams.get("min_price") ? Number(searchParams.get("min_price")) : undefined,
    max_price: searchParams.get("max_price") ? Number(searchParams.get("max_price")) : undefined,
    bedrooms: searchParams.get("bedrooms") ? Number(searchParams.get("bedrooms")) : undefined,
    sort_by: (searchParams.get("sort_by") as PropertyFilterParams["sort_by"]) || "newest",
    page: searchParams.get("page") ? Number(searchParams.get("page")) : 1,
    page_size: 10,
  });

  const [properties, setProperties] = useState<Property[]>([]);
  const [rankedItems, setRankedItems] = useState<RankedPropertyItem[]>([]);
  const [totalCount, setTotalCount] = useState<number>(0);
  const [totalPages, setTotalPages] = useState<number>(1);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [mobileView, setMobileView] = useState<"list" | "map">("list");
  const [selectedPropertyId, setSelectedPropertyId] = useState<string | number | null>(null);
  const [hoveredPropertyId, setHoveredPropertyId] = useState<string | number | null>(null);

  // Ranking preferences state
  const [rankingPrefs, setRankingPrefs] = useState<RankingPreferencesState>({
    presetKey: "balanced",
    weights: WEIGHT_PRESETS.balanced.weights,
    travel_mode: "driving",
  });
  const [showRankingPrefs, setShowRankingPrefs] = useState<boolean>(false);
  const [showAISearch, setShowAISearch] = useState<boolean>(false);
  const [showAskTheMap, setShowAskTheMap] = useState<boolean>(true);

  // Spatial search states
  const [showSearchThisArea, setShowSearchThisArea] = useState<boolean>(false);
  const [isSearchingArea, setIsSearchingArea] = useState<boolean>(false);
  const [activeViewportBounds, setActiveViewportBounds] = useState<MapBounds | null>(null);

  // POI Layer state
  const [selectedPOICategories, setSelectedPOICategories] = useState<Set<POICategory>>(new Set());
  const [pois, setPois] = useState<POIGeoJSONFeature[]>([]);
  const [isLoadingPOIs, setIsLoadingPOIs] = useState<boolean>(false);
  const [selectedPOIId, setSelectedPOIId] = useState<number | string | null>(null);
  const [showPOIFilter, setShowPOIFilter] = useState<boolean>(false);

  // Fetch POIs when viewport bounds or selected categories change
  useEffect(() => {
    if (selectedPOICategories.size === 0 || !activeViewportBounds) {
      setPois([]);
      return;
    }

    let cancelled = false;
    setIsLoadingPOIs(true);

    getMapPOIs({
      north: activeViewportBounds.north,
      south: activeViewportBounds.south,
      east: activeViewportBounds.east,
      west: activeViewportBounds.west,
      limit: 200,
    })
      .then((res) => {
        if (!cancelled) {
          const matching = (res.features || []).filter((f) =>
            selectedPOICategories.has(f.properties.category)
          );
          setPois(matching);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setPois([]);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setIsLoadingPOIs(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [activeViewportBounds, selectedPOICategories]);

  const fetchListings = useCallback(() => {
    setIsLoading(true);
    setErrorMessage(null);
    setShowSearchThisArea(false);

    if (filters.sort_by === "ranked") {
      // Deterministic Ranked Search
      const offset = ((filters.page || 1) - 1) * (filters.page_size || 10);
      searchRankedProperties({
        city: filters.city,
        locality: filters.locality,
        property_type: filters.property_type,
        min_price: filters.min_price,
        max_price: filters.max_price,
        bedrooms: filters.bedrooms,
        bathrooms: filters.bathrooms,
        status: filters.status,
        target_price: rankingPrefs.target_price,
        preferred_bedrooms: rankingPrefs.preferred_bedrooms,
        min_area_sqft: rankingPrefs.min_area_sqft,
        preferred_locality: filters.locality,
        destination: rankingPrefs.destination,
        travel_mode: rankingPrefs.travel_mode,
        weights: rankingPrefs.weights,
        limit: filters.page_size || 10,
        offset,
      })
        .then((res) => {
          setRankedItems(res.items || []);
          setProperties((res.items || []).map((i) => i.property));
          setTotalCount(res.total_candidates || 0);
          setTotalPages(res.total_pages || 1);
        })
        .catch((err) => {
          setErrorMessage(err instanceof Error ? err.message : "Failed to load ranked recommendations.");
          setRankedItems([]);
          setProperties([]);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      // Standard Filtered Search
      setRankedItems([]);
      listProperties(filters)
        .then((data) => {
          setProperties(data.items || []);
          setTotalCount(data.total || 0);
          setTotalPages(data.total_pages || 1);
        })
        .catch((err) => {
          setErrorMessage(err instanceof Error ? err.message : "Failed to load properties.");
        })
        .finally(() => {
          setIsLoading(false);
        });
    }
  }, [filters, rankingPrefs]);

  useEffect(() => {
    fetchListings();
  }, [fetchListings]);

  const handleFilterChange = (newFilters: Partial<PropertyFilterParams>) => {
    setFilters((prev) => ({
      ...prev,
      ...newFilters,
    }));
  };

  const handleResetFilters = () => {
    setFilters({
      page: 1,
      page_size: 10,
      sort_by: "newest",
    });
    setRankingPrefs({
      presetKey: "balanced",
      weights: WEIGHT_PRESETS.balanced.weights,
      travel_mode: "driving",
    });
    setShowRankingPrefs(false);
  };

  const handleApplyAIIntent = (intent: PropertySearchIntent) => {
    const newFilters: Partial<PropertyFilterParams> = {
      page: 1,
    };
    if (intent.city) newFilters.city = intent.city;
    if (intent.locality) newFilters.locality = intent.locality;
    if (intent.property_type) newFilters.property_type = intent.property_type;
    if (intent.min_price) newFilters.min_price = intent.min_price;
    if (intent.max_price) newFilters.max_price = intent.max_price;
    if (intent.bedrooms) newFilters.bedrooms = intent.bedrooms;

    if (intent.preferred_poi_categories && intent.preferred_poi_categories.length > 0) {
      const validCategories: POICategory[] = [
        "hospital",
        "school",
        "transit",
        "supermarket",
        "park",
        "pharmacy",
        "bank",
      ];
      const matched = intent.preferred_poi_categories.filter((c) =>
        validCategories.includes(c as POICategory)
      ) as POICategory[];
      if (matched.length > 0) {
        setSelectedPOICategories(new Set(matched));
      }
    }

    if (
      intent.commute_destination ||
      intent.min_area_sqft ||
      (intent.preferred_poi_categories && intent.preferred_poi_categories.length > 0)
    ) {
      setRankingPrefs((prev) => ({
        ...prev,
        target_price: (intent.max_price ?? undefined) || prev.target_price,
        preferred_bedrooms: (intent.bedrooms ?? undefined) || prev.preferred_bedrooms,
        min_area_sqft: (intent.min_area_sqft ?? undefined) || prev.min_area_sqft,
      }));
    }

    setFilters((prev) => ({
      ...prev,
      ...newFilters,
    }));
  };

  const handleAskMapResponse = (response: AskMapResponse) => {
    const nextState = response.state;

    // 1. Sync manual filters
    setFilters((prev) => ({
      ...prev,
      city: nextState.city ?? undefined,
      locality: nextState.locality ?? undefined,
      property_type: nextState.property_type ?? undefined,
      min_price: nextState.min_price ?? undefined,
      max_price: nextState.max_price ?? undefined,
      bedrooms: nextState.bedrooms ?? undefined,
      bathrooms: nextState.bathrooms ?? undefined,
      sort_by: response.action === "rank" || (response.items && response.items.length > 0) ? "ranked" : prev.sort_by,
      page: 1,
    }));

    // 2. Sync POI categories
    if (nextState.preferred_poi_categories) {
      setSelectedPOICategories(new Set(nextState.preferred_poi_categories));
    }

    // 3. Sync Ranking preferences
    setRankingPrefs((prev) => ({
      ...prev,
      destination: nextState.commute_destination
        ? {
            name: nextState.commute_destination,
            latitude: nextState.destination_lat || 12.926,
            longitude: nextState.destination_lng || 77.684,
          }
        : undefined,
      travel_mode: nextState.travel_mode || prev.travel_mode,
      presetKey: (nextState.ranking_preset as RankingPreferencesState["presetKey"]) || prev.presetKey,
      weights: nextState.ranking_weights || prev.weights || WEIGHT_PRESETS.balanced.weights,
      min_area_sqft: nextState.min_area_sqft ?? undefined,
      target_price: (nextState.max_price ?? undefined) || prev.target_price,
      preferred_bedrooms: (nextState.bedrooms ?? undefined) || prev.preferred_bedrooms,
    }));

    // 4. Update results directly if returned
    if (response.items && response.items.length > 0) {
      setRankedItems(response.items);
      setProperties(response.items.map((i) => i.property));
      setTotalCount(response.total_matches || response.items.length);
      setTotalPages(Math.max(1, Math.ceil((response.total_matches || response.items.length) / (filters.page_size || 10))));
    }
  };

  const handleCompareProperties = (ids: number[]) => {
    if (ids && ids.length > 0) {
      router.push(`/compare?ids=${ids.join(",")}`);
    }
  };

  const canonicalConversationalState: ConversationalSearchState = {
    min_price: filters.min_price ?? null,
    max_price: filters.max_price ?? null,
    bedrooms: filters.bedrooms ?? null,
    bathrooms: filters.bathrooms ?? null,
    min_area_sqft: rankingPrefs.min_area_sqft ?? null,
    property_type: filters.property_type ?? null,
    city: filters.city ?? null,
    locality: filters.locality ?? null,
    preferred_poi_categories: Array.from(selectedPOICategories),
    commute_destination: rankingPrefs.destination?.name ?? null,
    destination_lat: rankingPrefs.destination?.latitude ?? null,
    destination_lng: rankingPrefs.destination?.longitude ?? null,
    travel_mode: rankingPrefs.travel_mode || "driving",
    max_commute_minutes: null,
    viewport_bbox: activeViewportBounds
      ? {
          min_lat: activeViewportBounds.south,
          max_lat: activeViewportBounds.north,
          min_lng: activeViewportBounds.west,
          max_lng: activeViewportBounds.east,
        }
      : null,
    ranking_preset: rankingPrefs.presetKey || "balanced",
    ranking_weights: rankingPrefs.weights || WEIGHT_PRESETS.balanced.weights,
    selected_property_ids: selectedPropertyId ? [Number(selectedPropertyId)] : [],
  };

  const handlePageChange = (newPage: number) => {
    if (newPage >= 1 && newPage <= totalPages) {
      setFilters((prev) => ({ ...prev, page: newPage }));
    }
  };

  const handleSelectProperty = (property: Property | null) => {
    if (!property) {
      setSelectedPropertyId(null);
      return;
    }
    setSelectedPropertyId(property.id);
    const cardEl = document.getElementById(`property-card-${property.id}`);
    if (cardEl) {
      cardEl.scrollIntoView({ behavior: "smooth", block: "nearest" });
    }
  };

  // Viewport movement handler
  const handleViewportChange = (viewport: MapViewportState) => {
    if (viewport.bounds) {
      setActiveViewportBounds(viewport.bounds);
      setShowSearchThisArea(true);
    }
  };

  // Execute PostGIS Bounding Box search when "Search this area" is triggered
  const handleSearchThisArea = (bounds: MapBounds) => {
    setIsSearchingArea(true);
    setErrorMessage(null);

    if (filters.sort_by === "ranked") {
      searchRankedProperties({
        min_lat: bounds.south,
        min_lng: bounds.west,
        max_lat: bounds.north,
        max_lng: bounds.east,
        min_price: filters.min_price,
        max_price: filters.max_price,
        property_type: filters.property_type,
        bedrooms: filters.bedrooms,
        bathrooms: filters.bathrooms,
        status: filters.status,
        target_price: rankingPrefs.target_price,
        preferred_bedrooms: rankingPrefs.preferred_bedrooms,
        min_area_sqft: rankingPrefs.min_area_sqft,
        destination: rankingPrefs.destination,
        travel_mode: rankingPrefs.travel_mode,
        weights: rankingPrefs.weights,
        limit: 50,
        offset: 0,
      })
        .then((res) => {
          setRankedItems(res.items || []);
          setProperties((res.items || []).map((i) => i.property));
          setTotalCount(res.total_candidates || 0);
          setTotalPages(res.total_pages || 1);
          setShowSearchThisArea(false);
        })
        .catch((err) => {
          setErrorMessage(err instanceof Error ? err.message : "Failed to search this area.");
        })
        .finally(() => {
          setIsSearchingArea(false);
        });
    } else {
      searchPropertiesByBBox({
        min_lat: bounds.south,
        min_lng: bounds.west,
        max_lat: bounds.north,
        max_lng: bounds.east,
        min_price: filters.min_price,
        max_price: filters.max_price,
        property_type: filters.property_type,
        bedrooms: filters.bedrooms,
        bathrooms: filters.bathrooms,
        status: filters.status,
        sort_by: filters.sort_by,
        limit: 50,
        offset: 0,
      })
        .then((data) => {
          setRankedItems([]);
          setProperties(data.items || []);
          setTotalCount(data.total || 0);
          setTotalPages(data.total_pages || 1);
          setShowSearchThisArea(false);
        })
        .catch((err) => {
          setErrorMessage(err instanceof Error ? err.message : "Failed to search this area.");
        })
        .finally(() => {
          setIsSearchingArea(false);
        });
    }
  };

  // Compute map center from active results or city default
  const centerLat =
    properties.length > 0 && properties[0].latitude
      ? properties[0].latitude
      : filters.city?.toLowerCase() === "chennai"
      ? 13.0418
      : 12.9716;
  const centerLng =
    properties.length > 0 && properties[0].longitude
      ? properties[0].longitude
      : filters.city?.toLowerCase() === "chennai"
      ? 80.2341
      : 77.5946;

  return (
    <div className="flex flex-1 flex-col h-[calc(100vh-3.5rem)] overflow-hidden">
      {/* Top Search & Filter Bar */}
      <div className="shrink-0 border-b border-border bg-card">
        <div className="mx-auto max-w-7xl px-4 py-2 sm:px-6">
          <div className="flex items-center justify-between gap-3">
            <div className="flex items-center gap-2.5 flex-1">
              <SearchBar
                initialValue={filters.locality || filters.city || ""}
                placeholder="Search by locality or city (e.g. Chennai, Adyar, OMR)..."
                onSearch={(query) => {
                  const trimmed = query?.trim() || "";
                  if (!trimmed) {
                    handleFilterChange({
                      city: undefined,
                      locality: undefined,
                      page: 1,
                    });
                  } else if (
                    trimmed.toLowerCase() === "chennai" ||
                    trimmed.toLowerCase() === "bengaluru" ||
                    trimmed.toLowerCase() === "bangalore"
                  ) {
                    handleFilterChange({
                      city: trimmed.toLowerCase() === "bangalore" ? "Bengaluru" : trimmed,
                      locality: undefined,
                      page: 1,
                    });
                  } else {
                    handleFilterChange({
                      locality: trimmed,
                      page: 1,
                    });
                  }
                }}
                className="max-w-md"
              />
              <Button
                type="button"
                variant={showAskTheMap ? "default" : "outline"}
                size="sm"
                onClick={() => setShowAskTheMap(!showAskTheMap)}
                className="h-10 gap-1.5 text-xs font-semibold shrink-0"
              >
                <Sparkles className="h-4 w-4" />
                <span>{showAskTheMap ? "Hide Ask the Map" : "Ask the Map"}</span>
              </Button>
            </div>
          </div>
          {showAskTheMap && (
            <div className="mt-3 pb-1">
              <AskTheMapBar
                currentState={canonicalConversationalState}
                mapViewport={
                  activeViewportBounds
                    ? {
                        min_lat: activeViewportBounds.south,
                        max_lat: activeViewportBounds.north,
                        min_lng: activeViewportBounds.west,
                        max_lng: activeViewportBounds.east,
                      }
                    : null
                }
                onResponse={handleAskMapResponse}
                onCompare={handleCompareProperties}
              />
            </div>
          )}
          {showAISearch && (
            <div className="mt-3 pb-1">
              <NaturalLanguageSearch onApplyIntent={handleApplyAIIntent} />
            </div>
          )}
        </div>
        <FilterBar
          filters={filters}
          onFilterChange={handleFilterChange}
          onReset={handleResetFilters}
          totalResults={totalCount}
        />
      </div>

      {/* Main Split Layout: Results Column + Map Viewport */}
      <div className="relative flex flex-1 overflow-hidden">
        {/* Left Results Column */}
        <section
          className={`flex flex-col w-full lg:w-[55%] xl:w-[50%] h-full overflow-y-auto border-r border-border bg-background p-4 sm:p-6 ${
            mobileView === "map" ? "hidden lg:flex" : "flex"
          }`}
        >
          {/* Ranking Preferences Header Banner if in Ranked Mode */}
          {filters.sort_by === "ranked" && (
            <div className="mb-4 space-y-3">
              <div className="flex items-center justify-between rounded-lg border border-emerald-500/30 bg-emerald-500/5 p-3">
                <div className="flex items-center gap-2">
                  <Sparkles className="h-4 w-4 text-emerald-500 shrink-0" />
                  <div>
                    <span className="text-xs font-bold text-foreground">
                      Deterministic Multi-Factor Ranking Active
                    </span>
                    <p className="text-[11px] text-muted-foreground">
                      Properties scored across price, bedrooms, area, POIs, and commute.
                    </p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => setShowRankingPrefs(!showRankingPrefs)}
                  className="h-8 gap-1 text-xs border-emerald-500/30 hover:bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                >
                  <SlidersHorizontal className="h-3 w-3" />
                  <span>{showRankingPrefs ? "Hide Preferences" : "Tune Preferences"}</span>
                </Button>
              </div>

              {/* Collapsible Ranking Preferences Panel */}
              {showRankingPrefs && (
                <RankingPreferences
                  preferences={rankingPrefs}
                  city={filters.city}
                  onChange={(newPrefs) => setRankingPrefs(newPrefs)}
                  onClose={() => setShowRankingPrefs(false)}
                />
              )}
            </div>
          )}

          {errorMessage ? (
            <ErrorState
              title="Search Error"
              message={errorMessage}
              onRetry={fetchListings}
            />
          ) : (
            <>
              <div className="flex-1">
                <PropertyGrid
                  properties={properties}
                  rankedItems={filters.sort_by === "ranked" ? rankedItems : undefined}
                  isLoading={isLoading || isSearchingArea}
                  columns={2}
                  skeletonCount={6}
                  savedIds={savedIds}
                  selectedPropertyId={selectedPropertyId}
                  hoveredPropertyId={hoveredPropertyId}
                  onSelectProperty={handleSelectProperty}
                  onHoverProperty={(p) => setHoveredPropertyId(p ? p.id : null)}
                  onToggleSave={(id) => {
                    const p =
                      properties.find((x) => x.id === id) ||
                      rankedItems.find((x) => x.property.id === id)?.property;
                    if (p) toggleSave(p);
                  }}
                />
              </div>

              {/* Pagination Controls */}
              {totalPages > 1 && (
                <div className="mt-8 flex items-center justify-between border-t border-border pt-4">
                  <div className="text-xs text-muted-foreground">
                    Page <span className="font-semibold text-foreground">{filters.page}</span> of{" "}
                    <span className="font-semibold text-foreground">{totalPages}</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange((filters.page || 1) - 1)}
                      disabled={(filters.page || 1) <= 1 || isLoading || isSearchingArea}
                      className="h-8 gap-1 text-xs"
                    >
                      <ChevronLeft className="h-3.5 w-3.5" />
                      <span>Previous</span>
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handlePageChange((filters.page || 1) + 1)}
                      disabled={(filters.page || 1) >= totalPages || isLoading || isSearchingArea}
                      className="h-8 gap-1 text-xs"
                    >
                      <span>Next</span>
                      <ChevronRight className="h-3.5 w-3.5" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </section>

        {/* Right Map Container Boundary */}
        <section
          className={`relative flex-1 h-full p-2 bg-muted/10 ${
            mobileView === "list" ? "hidden lg:flex" : "flex"
          }`}
        >
          {/* Floating POI Filter Widget */}
          <div className="absolute top-4 left-4 z-20">
            {showPOIFilter ? (
              <div className="relative">
                <POIFilter
                  selectedCategories={selectedPOICategories}
                  onCategoryChange={setSelectedPOICategories}
                  isLoading={isLoadingPOIs}
                  className="w-48 shadow-md backdrop-blur-xs"
                />
                <button
                  type="button"
                  onClick={() => setShowPOIFilter(false)}
                  className="mt-1 text-[10px] text-muted-foreground hover:text-foreground underline px-1 cursor-pointer"
                >
                  Close places filter
                </button>
              </div>
            ) : (
              <Button
                size="sm"
                variant="outline"
                onClick={() => setShowPOIFilter(true)}
                className="rounded-full bg-background/90 hover:bg-background text-foreground border border-border/80 shadow-xs backdrop-blur-xs px-3 py-1 text-xs font-semibold flex items-center gap-1.5 cursor-pointer"
              >
                <span>Nearby Places</span>
                {selectedPOICategories.size > 0 && (
                  <span className="flex h-4 w-4 items-center justify-center rounded-full bg-emerald-600 text-[10px] text-white font-bold">
                    {selectedPOICategories.size}
                  </span>
                )}
              </Button>
            )}
          </div>

          <MapContainer
            properties={properties}
            pois={pois}
            selectedPropertyId={selectedPropertyId ? String(selectedPropertyId) : null}
            hoveredPropertyId={hoveredPropertyId ? String(hoveredPropertyId) : null}
            selectedPOIId={selectedPOIId}
            onSelectProperty={(p) => {
              setSelectedPOIId(null);
              handleSelectProperty(p);
            }}
            onHoverProperty={(p) => setHoveredPropertyId(p ? p.id : null)}
            onSelectPOI={(poi) => setSelectedPOIId(poi ? poi.id : null)}
            onViewportChange={handleViewportChange}
            onSearchThisArea={handleSearchThisArea}
            showSearchThisArea={showSearchThisArea}
            isSearchingArea={isSearchingArea}
            latitude={centerLat}
            longitude={centerLng}
            zoom={12}
            interactive={true}
          />
        </section>
      </div>

      {/* Floating Mobile Toggle Switch */}
      <div className="lg:hidden fixed bottom-6 left-1/2 -translate-x-1/2 z-30 shadow-lg">
        <div className="flex items-center rounded-full border border-border bg-card p-1 shadow-md">
          <Button
            size="sm"
            variant={mobileView === "list" ? "default" : "ghost"}
            onClick={() => setMobileView("list")}
            className="rounded-full h-8 px-4 text-xs font-medium gap-1.5"
          >
            <List className="h-3.5 w-3.5" />
            <span>List</span>
          </Button>
          <Button
            size="sm"
            variant={mobileView === "map" ? "default" : "ghost"}
            onClick={() => setMobileView("map")}
            className="rounded-full h-8 px-4 text-xs font-medium gap-1.5"
          >
            <MapIcon className="h-3.5 w-3.5" />
            <span>Map</span>
          </Button>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<LoadingState title="Loading discovery search..." />}>
      <SearchContent />
    </Suspense>
  );
}

