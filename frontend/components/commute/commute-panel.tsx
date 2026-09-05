"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Car,
  Bike,
  Footprints,
  Navigation,
  Clock,
  MapPin,
  Route,
  Zap,
  RotateCcw,
  Plus,
  Loader2,
  CheckCircle2,
  Server,
} from "lucide-react";
import { getCityDestinations } from "@/lib/constants/destinations";
import { getPropertyCommute } from "@/lib/api/commute";
import type { CommuteDestination, CommuteResponse, TravelMode } from "@/types";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";

const TRAVEL_MODES: { mode: TravelMode; label: string; icon: React.ElementType }[] = [
  { mode: "driving", label: "Drive", icon: Car },
  { mode: "cycling", label: "Cycle", icon: Bike },
  { mode: "walking", label: "Walk", icon: Footprints },
];

interface CommutePanelProps {
  propertyId: number;
  propertyCity?: string;
  latitude?: number;
  longitude?: number;
  onRouteCalculated?: (route: CommuteResponse | null) => void;
  className?: string;
}

export function CommutePanel({
  propertyId,
  propertyCity,
  latitude,
  longitude,
  onRouteCalculated,
  className = "",
}: CommutePanelProps) {
  const presetDestinations = React.useMemo(() => {
    return getCityDestinations(propertyCity, latitude, longitude);
  }, [propertyCity, latitude, longitude]);

  const [selectedDestination, setSelectedDestination] = useState<CommuteDestination>(
    presetDestinations[0]
  );

  useEffect(() => {
    setSelectedDestination((prev) => {
      const exists = presetDestinations.some(
        (p) => p.name === prev.name && p.latitude === prev.latitude
      );
      return exists ? prev : presetDestinations[0];
    });
  }, [presetDestinations]);

  const [travelMode, setTravelMode] = useState<TravelMode>("driving");
  const [commuteResult, setCommuteResult] = useState<CommuteResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Custom destination modal / inline form state
  const [isCustom, setIsCustom] = useState<boolean>(false);
  const [customName, setCustomName] = useState<string>("");
  const [customLat, setCustomLat] = useState<string>("");
  const [customLng, setCustomLng] = useState<string>("");

  const fetchCommute = useCallback(
    async (dest: CommuteDestination, mode: TravelMode) => {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const result = await getPropertyCommute(propertyId, {
          destination_lat: dest.latitude,
          destination_lng: dest.longitude,
          destination_name: dest.name,
          mode,
        });
        setCommuteResult(result);
        onRouteCalculated?.(result);
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Failed to calculate road commute route.";
        setErrorMessage(msg);
        setCommuteResult(null);
        onRouteCalculated?.(null);
      } finally {
        setIsLoading(false);
      }
    },
    [propertyId, onRouteCalculated]
  );

  // Automatically calculate commute for initial default preset
  useEffect(() => {
    fetchCommute(selectedDestination, travelMode);
  }, [fetchCommute, selectedDestination, travelMode]);

  const handleSelectPreset = (dest: CommuteDestination) => {
    setIsCustom(false);
    setSelectedDestination(dest);
  };

  const handleApplyCustomDestination = (e: React.FormEvent) => {
    e.preventDefault();
    const lat = parseFloat(customLat);
    const lng = parseFloat(customLng);

    if (!customName.trim()) {
      setErrorMessage("Please enter a destination name.");
      return;
    }
    if (isNaN(lat) || lat < -90 || lat > 90) {
      setErrorMessage("Please enter a valid latitude (-90 to 90).");
      return;
    }
    if (isNaN(lng) || lng < -180 || lng > 180) {
      setErrorMessage("Please enter a valid longitude (-180 to 180).");
      return;
    }

    const customDest: CommuteDestination = {
      name: customName.trim(),
      latitude: lat,
      longitude: lng,
    };
    setSelectedDestination(customDest);
    setIsCustom(false);
  };

  const handleClearRoute = () => {
    setCommuteResult(null);
    onRouteCalculated?.(null);
  };

  return (
    <Card className={`border-border bg-card shadow-sm ${className}`}>
      <CardHeader className="pb-3 border-b border-border/60">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Route className="h-5 w-5 text-primary" />
            <CardTitle className="text-base font-bold text-foreground tracking-tight">
              Commute & Travel Intelligence
            </CardTitle>
          </div>
          <Badge variant="outline" className="text-[10px] font-medium tracking-wide">
            ROAD NETWORK ROUTING
          </Badge>
        </div>
        <p className="text-xs text-muted-foreground mt-1">
          Real-world road distance and travel duration calculated via routing network.
        </p>
      </CardHeader>

      <CardContent className="space-y-5 pt-4">
        {/* Travel Mode Selector */}
        <div className="space-y-1.5">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
            Travel Mode
          </label>
          <div className="grid grid-cols-3 gap-2">
            {TRAVEL_MODES.map(({ mode, label, icon: Icon }) => (
              <Button
                key={mode}
                type="button"
                variant={travelMode === mode ? "default" : "outline"}
                size="sm"
                className={`h-9 gap-1.5 text-xs font-semibold ${
                  travelMode === mode
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground"
                }`}
                onClick={() => setTravelMode(mode)}
              >
                <Icon className="h-3.5 w-3.5" />
                <span>{label}</span>
              </Button>
            ))}
          </div>
        </div>

        {/* Destination Presets */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
              Select Destination
            </label>
            <button
              type="button"
              onClick={() => setIsCustom(!isCustom)}
              className="inline-flex items-center gap-1 text-[11px] font-medium text-primary hover:underline"
            >
              <Plus className="h-3 w-3" />
              <span>{isCustom ? "Show Presets" : "Custom Target"}</span>
            </button>
          </div>

          {!isCustom ? (
            <div className="flex flex-wrap gap-1.5">
              {presetDestinations.map((dest) => {
                const isSelected =
                  selectedDestination.name === dest.name &&
                  selectedDestination.latitude === dest.latitude;
                return (
                  <button
                    key={dest.name}
                    type="button"
                    onClick={() => handleSelectPreset(dest)}
                    className={`inline-flex items-center gap-1.5 rounded-md px-2.5 py-1.5 text-xs font-medium transition-all ${
                      isSelected
                        ? "bg-primary/15 text-primary border border-primary/30 font-semibold"
                        : "bg-muted/50 text-muted-foreground border border-border hover:bg-muted hover:text-foreground"
                    }`}
                  >
                    <MapPin className="h-3 w-3 shrink-0" />
                    <span>{dest.name}</span>
                  </button>
                );
              })}
            </div>
          ) : (
            <form
              onSubmit={handleApplyCustomDestination}
              className="rounded-lg border border-border bg-muted/20 p-3 space-y-3 text-xs"
            >
              <div className="space-y-1">
                <span className="font-medium text-foreground">Destination Name</span>
                <Input
                  placeholder="e.g. Workplace, College, Metro"
                  value={customName}
                  onChange={(e) => setCustomName(e.target.value)}
                  className="h-8 text-xs"
                />
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="space-y-1">
                  <span className="font-medium text-foreground">Latitude</span>
                  <Input
                    placeholder="12.9716"
                    value={customLat}
                    onChange={(e) => setCustomLat(e.target.value)}
                    className="h-8 text-xs font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <span className="font-medium text-foreground">Longitude</span>
                  <Input
                    placeholder="77.5946"
                    value={customLng}
                    onChange={(e) => setCustomLng(e.target.value)}
                    className="h-8 text-xs font-mono"
                  />
                </div>
              </div>
              <Button type="submit" size="sm" className="h-8 w-full text-xs font-semibold">
                Calculate Custom Route
              </Button>
            </form>
          )}
        </div>

        {/* Error message */}
        {errorMessage && (
          <div className="rounded-md border border-destructive/20 bg-destructive/10 p-3 text-xs text-destructive">
            {errorMessage}
          </div>
        )}

        {/* Loading state */}
        {isLoading && (
          <div className="flex items-center justify-center gap-2 rounded-lg border border-border bg-muted/20 py-6 text-xs text-muted-foreground">
            <Loader2 className="h-4 w-4 animate-spin text-primary" />
            <span>Calculating road network path & duration...</span>
          </div>
        )}

        {/* Result Card */}
        {!isLoading && commuteResult && (
          <div className="rounded-lg border border-border bg-card p-4 space-y-3.5 shadow-sm">
            {/* Header with destination and route status */}
            <div className="flex items-start justify-between gap-2">
              <div>
                <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                  Route to
                </span>
                <h4 className="text-sm font-bold text-foreground">
                  {commuteResult.destination.name}
                </h4>
              </div>
              <div className="flex items-center gap-1.5">
                {commuteResult.cached && (
                  <Badge variant="secondary" className="gap-1 text-[10px] font-semibold text-emerald-600 bg-emerald-500/10 border-emerald-500/20">
                    <Zap className="h-2.5 w-2.5" />
                    Cached
                  </Badge>
                )}
                <Badge variant="outline" className="text-[10px] font-mono text-muted-foreground">
                  {commuteResult.provider}
                </Badge>
              </div>
            </div>

            {/* Metric Boxes: Duration & Distance */}
            <div className="grid grid-cols-2 gap-3">
              <div className="flex flex-col rounded-md border border-border bg-muted/30 p-3">
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Clock className="h-3.5 w-3.5 text-primary" />
                  <span className="font-medium">Est. Travel Time</span>
                </div>
                <div className="mt-1 flex items-baseline gap-1">
                  <span className="text-2xl font-extrabold text-foreground tracking-tight">
                    {commuteResult.duration_minutes}
                  </span>
                  <span className="text-xs font-semibold text-muted-foreground">min</span>
                </div>
              </div>

              <div className="flex flex-col rounded-md border border-border bg-muted/30 p-3">
                <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                  <Navigation className="h-3.5 w-3.5 text-primary" />
                  <span className="font-medium">Road Distance</span>
                </div>
                <div className="mt-1 flex items-baseline gap-1">
                  <span className="text-2xl font-extrabold text-foreground tracking-tight">
                    {commuteResult.distance_km}
                  </span>
                  <span className="text-xs font-semibold text-muted-foreground">km</span>
                </div>
              </div>
            </div>

            {/* Summary description */}
            {commuteResult.summary && (
              <div className="flex items-center gap-2 rounded-md bg-muted/40 px-3 py-2 text-xs text-muted-foreground">
                <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 shrink-0" />
                <span className="truncate">{commuteResult.summary}</span>
              </div>
            )}

            {/* Waypoints / coordinates info */}
            <div className="flex items-center justify-between border-t border-border/60 pt-2 text-[11px] text-muted-foreground">
              <span className="font-mono">
                {commuteResult.geometry.coordinates.length} waypoints on map
              </span>
              <button
                type="button"
                onClick={handleClearRoute}
                className="inline-flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground"
              >
                <RotateCcw className="h-3 w-3" />
                <span>Reset Route</span>
              </button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
