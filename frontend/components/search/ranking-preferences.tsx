"use client";

import React, { useState } from "react";
import { Sliders, Sparkles, MapPin, Car, Bike, Footprints, RotateCcw, X } from "lucide-react";
import { CommuteDestination, RankingWeights, TravelMode } from "@/types";
import {
  getCityDestinations,
  BENGALURU_DESTINATIONS,
  CHENNAI_DESTINATIONS,
} from "@/lib/constants/destinations";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";

export const RANKING_COMMUTE_PRESETS: CommuteDestination[] = [
  ...BENGALURU_DESTINATIONS,
  ...CHENNAI_DESTINATIONS,
];

export const WEIGHT_PRESETS: Record<string, { label: string; weights: RankingWeights }> = {
  balanced: {
    label: "Balanced",
    weights: { price: 0.25, bedrooms: 0.2, area: 0.15, location: 0.15, commute: 0.15, locality: 0.1 },
  },
  budget: {
    label: "Budget First",
    weights: { price: 0.45, bedrooms: 0.15, area: 0.15, location: 0.1, commute: 0.1, locality: 0.05 },
  },
  commute: {
    label: "Commute First",
    weights: { price: 0.15, bedrooms: 0.1, area: 0.1, location: 0.15, commute: 0.4, locality: 0.1 },
  },
  location: {
    label: "POIs & Amenities",
    weights: { price: 0.15, bedrooms: 0.15, area: 0.1, location: 0.35, commute: 0.15, locality: 0.1 },
  },
};

export interface RankingPreferencesState {
  target_price?: number;
  preferred_bedrooms?: number;
  min_area_sqft?: number;
  destination?: CommuteDestination;
  travel_mode?: TravelMode;
  weights?: RankingWeights;
  presetKey?: string;
}

interface RankingPreferencesProps {
  preferences: RankingPreferencesState;
  city?: string;
  onChange: (prefs: RankingPreferencesState) => void;
  onClose?: () => void;
  className?: string;
}

export function RankingPreferences({
  preferences,
  city,
  onChange,
  onClose,
  className = "",
}: RankingPreferencesProps) {
  const destinations = React.useMemo(() => {
    return city ? getCityDestinations(city) : RANKING_COMMUTE_PRESETS;
  }, [city]);

  const [selectedPreset, setSelectedPreset] = useState<string>(
    preferences.presetKey || "balanced"
  );

  const handlePresetSelect = (presetKey: string) => {
    setSelectedPreset(presetKey);
    const preset = WEIGHT_PRESETS[presetKey];
    if (preset) {
      onChange({
        ...preferences,
        presetKey,
        weights: preset.weights,
      });
    }
  };

  const handleDestinationSelect = (dest: CommuteDestination | undefined) => {
    onChange({
      ...preferences,
      destination: dest,
    });
  };

  const handleReset = () => {
    setSelectedPreset("balanced");
    onChange({
      target_price: undefined,
      preferred_bedrooms: undefined,
      min_area_sqft: undefined,
      destination: undefined,
      travel_mode: "driving",
      weights: WEIGHT_PRESETS.balanced.weights,
      presetKey: "balanced",
    });
  };

  return (
    <div className={`rounded-xl border border-border bg-card p-4 shadow-lg space-y-4 text-xs ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/60 pb-2.5">
        <div className="flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-emerald-500" />
          <h3 className="text-sm font-bold text-foreground">Match & Ranking Preferences</h3>
          <Badge variant="outline" className="text-[10px] font-semibold text-emerald-600 border-emerald-500/30">
            DETERMINISTIC
          </Badge>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={handleReset}
            className="flex items-center gap-1 text-[11px] text-muted-foreground hover:text-foreground"
          >
            <RotateCcw className="h-3 w-3" />
            <span>Reset</span>
          </button>
          {onClose && (
            <button
              type="button"
              onClick={onClose}
              className="text-muted-foreground hover:text-foreground p-1"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>

      {/* Weight Profiles */}
      <div className="space-y-1.5">
        <label className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground">
          Priority Profile
        </label>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-1.5">
          {Object.entries(WEIGHT_PRESETS).map(([key, config]) => (
            <button
              key={key}
              type="button"
              onClick={() => handlePresetSelect(key)}
              className={`rounded-md px-2.5 py-1.5 text-xs font-semibold text-center border transition-all ${
                selectedPreset === key
                  ? "bg-primary text-primary-foreground border-primary shadow-xs"
                  : "bg-muted/50 text-muted-foreground border-border hover:bg-muted hover:text-foreground"
              }`}
            >
              {config.label}
            </button>
          ))}
        </div>
      </div>

      {/* Target Criteria Inputs */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
        {/* Target Price */}
        <div className="space-y-1">
          <label className="text-[11px] font-medium text-foreground">Target Budget</label>
          <Select
            value={preferences.target_price ? String(preferences.target_price) : ""}
            onChange={(e) =>
              onChange({
                ...preferences,
                target_price: e.target.value ? Number(e.target.value) : undefined,
              })
            }
          >
            <option value="">No Target Budget</option>
            <option value="4000000">₹40 Lakh</option>
            <option value="6000000">₹60 Lakh</option>
            <option value="8000000">₹80 Lakh</option>
            <option value="10000000">₹1.0 Crore</option>
            <option value="12500000">₹1.25 Crore</option>
            <option value="15000000">₹1.50 Crore</option>
            <option value="20000000">₹2.0 Crore</option>
            <option value="30000000">₹3.0 Crore</option>
          </Select>
        </div>

        {/* Preferred Bedrooms */}
        <div className="space-y-1">
          <label className="text-[11px] font-medium text-foreground">Preferred BHK</label>
          <Select
            value={preferences.preferred_bedrooms !== undefined ? String(preferences.preferred_bedrooms) : ""}
            onChange={(e) =>
              onChange({
                ...preferences,
                preferred_bedrooms: e.target.value ? Number(e.target.value) : undefined,
              })
            }
          >
            <option value="">Any BHK</option>
            <option value="1">1 BHK</option>
            <option value="2">2 BHK</option>
            <option value="3">3 BHK</option>
            <option value="4">4 BHK</option>
          </Select>
        </div>

        {/* Min Area */}
        <div className="space-y-1">
          <label className="text-[11px] font-medium text-foreground">Min Area (sq.ft)</label>
          <Input
            type="number"
            placeholder="e.g. 1000"
            value={preferences.min_area_sqft || ""}
            onChange={(e) =>
              onChange({
                ...preferences,
                min_area_sqft: e.target.value ? Number(e.target.value) : undefined,
              })
            }
            className="h-9 text-xs"
          />
        </div>
      </div>

      {/* Commute Target Hub */}
      <div className="space-y-2 pt-1 border-t border-border/60">
        <div className="flex items-center justify-between">
          <label className="text-[11px] font-semibold uppercase tracking-wider text-muted-foreground flex items-center gap-1">
            <MapPin className="h-3 w-3 text-primary" />
            Commute Destination (Office / Hub)
          </label>
          {preferences.destination && (
            <button
              type="button"
              onClick={() => handleDestinationSelect(undefined)}
              className="text-[10px] text-muted-foreground hover:text-foreground underline"
            >
              Clear Destination
            </button>
          )}
        </div>

        <div className="flex flex-wrap gap-1.5">
          {destinations.map((dest) => {
            const isSelected =
              preferences.destination?.name === dest.name &&
              preferences.destination?.latitude === dest.latitude;
            return (
              <button
                key={dest.name}
                type="button"
                onClick={() => handleDestinationSelect(isSelected ? undefined : dest)}
                className={`rounded-md px-2.5 py-1 text-xs font-medium border transition-all ${
                  isSelected
                    ? "bg-emerald-500/15 text-emerald-600 dark:text-emerald-400 border-emerald-500/30 font-semibold shadow-2xs"
                    : "bg-muted/40 text-muted-foreground border-border hover:bg-muted hover:text-foreground"
                }`}
              >
                {dest.name}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
