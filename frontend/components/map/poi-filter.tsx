"use client";

import React from "react";
import type { POICategory } from "@/types";
import { POI_CATEGORIES, POI_CATEGORY_LABELS } from "@/types";

interface POIFilterProps {
  selectedCategories: Set<POICategory>;
  onCategoryChange: (categories: Set<POICategory>) => void;
  isLoading?: boolean;
  className?: string;
}

/** Category colour indicators — same palette as poi-marker.tsx. */
const CATEGORY_DOT_COLORS: Record<POICategory, string> = {
  hospital: "bg-red-500",
  school: "bg-blue-500",
  transit: "bg-orange-500",
  supermarket: "bg-teal-500",
  park: "bg-emerald-500",
  pharmacy: "bg-purple-500",
  bank: "bg-slate-500",
};

/**
 * Compact POI category filter panel for the map sidebar.
 * Renders a checkbox list — selecting a category triggers a new POI fetch.
 * Uses controlled state: parent owns `selectedCategories`.
 */
export function POIFilter({
  selectedCategories,
  onCategoryChange,
  isLoading = false,
  className = "",
}: POIFilterProps) {
  const toggleCategory = (category: POICategory) => {
    const next = new Set(selectedCategories);
    if (next.has(category)) {
      next.delete(category);
    } else {
      next.add(category);
    }
    onCategoryChange(next);
  };

  const allSelected = selectedCategories.size === POI_CATEGORIES.length;

  const toggleAll = () => {
    if (allSelected) {
      onCategoryChange(new Set());
    } else {
      onCategoryChange(new Set(POI_CATEGORIES));
    }
  };

  return (
    <div
      className={`rounded-lg border border-border bg-card shadow-sm ${className}`}
      aria-label="Points of Interest category filter"
    >
      <div className="flex items-center justify-between px-3 py-2 border-b border-border/60">
        <span className="text-[11px] font-semibold text-foreground uppercase tracking-wider">
          Nearby Places
        </span>
        <button
          type="button"
          onClick={toggleAll}
          className="text-[10px] font-medium text-muted-foreground hover:text-foreground transition-colors cursor-pointer"
          aria-label={allSelected ? "Deselect all categories" : "Select all categories"}
        >
          {allSelected ? "Clear all" : "Select all"}
        </button>
      </div>

      <div className="p-2 space-y-0.5">
        {POI_CATEGORIES.map((category) => {
          const isChecked = selectedCategories.has(category);
          return (
            <label
              key={category}
              className={`
                flex items-center gap-2.5 rounded-md px-2 py-1.5 cursor-pointer select-none
                text-xs transition-colors
                ${isChecked
                  ? "bg-muted/60 text-foreground"
                  : "text-muted-foreground hover:bg-muted/40 hover:text-foreground"
                }
              `}
              aria-label={`${isChecked ? "Hide" : "Show"} ${POI_CATEGORY_LABELS[category]}`}
            >
              <input
                type="checkbox"
                checked={isChecked}
                onChange={() => toggleCategory(category)}
                disabled={isLoading}
                className="sr-only"
                aria-hidden="true"
              />
              {/* Coloured dot as visual checkbox replacement */}
              <span
                className={`
                  flex h-3.5 w-3.5 shrink-0 items-center justify-center rounded border transition-all
                  ${isChecked
                    ? "border-transparent"
                    : "border-border bg-background"
                  }
                `}
              >
                {isChecked && (
                  <span
                    className={`h-2 w-2 rounded-sm ${CATEGORY_DOT_COLORS[category]}`}
                    aria-hidden="true"
                  />
                )}
              </span>
              <span className="font-medium">{POI_CATEGORY_LABELS[category]}</span>
              {/* Colour legend dot */}
              <span
                className={`ml-auto h-2 w-2 shrink-0 rounded-full ${
                  isChecked ? CATEGORY_DOT_COLORS[category] : "bg-muted-foreground/30"
                } transition-colors`}
                aria-hidden="true"
              />
            </label>
          );
        })}
      </div>

      {isLoading && (
        <div className="border-t border-border/60 px-3 py-1.5 text-[10px] text-muted-foreground">
          Loading places...
        </div>
      )}
    </div>
  );
}
