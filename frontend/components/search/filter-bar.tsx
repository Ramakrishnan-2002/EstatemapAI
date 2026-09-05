"use client";

import React from "react";
import { SlidersHorizontal, RotateCcw } from "lucide-react";
import { PropertyFilterParams } from "@/types";
import { Button } from "@/components/ui/button";
import { Select } from "@/components/ui/select";
import { cn } from "@/lib/utils";

interface FilterBarProps {
  filters: PropertyFilterParams;
  onFilterChange: (newFilters: Partial<PropertyFilterParams>) => void;
  onReset: () => void;
  className?: string;
  totalResults?: number;
}

export function FilterBar({
  filters,
  onFilterChange,
  onReset,
  className,
  totalResults,
}: FilterBarProps) {
  const hasActiveFilters = Boolean(
    filters.city ||
      filters.locality ||
      filters.property_type ||
      filters.min_price ||
      filters.max_price ||
      filters.bedrooms ||
      (filters.sort_by && filters.sort_by !== "newest")
  );

  return (
    <div
      className={cn(
        "flex flex-wrap items-center justify-between gap-3 border-b border-border bg-card/60 px-4 py-3 backdrop-blur-sm",
        className
      )}
    >
      {/* Primary Quick Filters */}
      <div className="flex flex-wrap items-center gap-2">
        {/* Property Type */}
        <div className="w-36">
          <Select
            value={filters.property_type || ""}
            onChange={(e) =>
              onFilterChange({
                property_type: e.target.value || undefined,
                page: 1,
              })
            }
          >
            <option value="">All Types</option>
            <option value="apartment">Apartment</option>
            <option value="villa">Villa</option>
            <option value="independent_house">Independent House</option>
            <option value="plot">Plot / Land</option>
            <option value="commercial">Commercial</option>
          </Select>
        </div>

        {/* Bedrooms */}
        <div className="w-32">
          <Select
            value={filters.bedrooms !== undefined && filters.bedrooms !== null ? filters.bedrooms.toString() : ""}
            onChange={(e) =>
              onFilterChange({
                bedrooms: e.target.value ? parseInt(e.target.value, 10) : undefined,
                page: 1,
              })
            }
          >
            <option value="">Any BHK</option>
            <option value="1">1 BHK</option>
            <option value="2">2 BHK</option>
            <option value="3">3 BHK</option>
            <option value="4">4+ BHK</option>
          </Select>
        </div>

        {/* Max Budget */}
        <div className="w-36">
          <Select
            value={filters.max_price ? filters.max_price.toString() : ""}
            onChange={(e) =>
              onFilterChange({
                max_price: e.target.value ? parseFloat(e.target.value) : undefined,
                page: 1,
              })
            }
          >
            <option value="">Max Budget</option>
            <option value="5000000">Under ₹50 Lakh</option>
            <option value="10000000">Under ₹1 Crore</option>
            <option value="15000000">Under ₹1.5 Crore</option>
            <option value="25000000">Under ₹2.5 Crore</option>
            <option value="50000000">Under ₹5 Crore</option>
          </Select>
        </div>

        {/* Sort By */}
        <div className="w-44">
          <Select
            value={filters.sort_by || "newest"}
            onChange={(e) =>
              onFilterChange({
                sort_by: (e.target.value as PropertyFilterParams["sort_by"]) || "newest",
                page: 1,
              })
            }
          >
            <option value="newest">Newest First</option>
            <option value="ranked">✨ Best Match (Ranked)</option>
            <option value="price_asc">Price: Low to High</option>
            <option value="price_desc">Price: High to Low</option>
            <option value="area_asc">Area: Low to High</option>
            <option value="area_desc">Area: High to Low</option>
          </Select>
        </div>

        {/* Reset Filter Button */}
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={onReset}
            className="h-9 gap-1 text-xs text-muted-foreground hover:text-foreground"
          >
            <RotateCcw className="h-3.5 w-3.5" />
            <span>Reset</span>
          </Button>
        )}
      </div>

      {/* Results Count Counter */}
      {totalResults !== undefined && (
        <div className="text-xs font-medium text-muted-foreground">
          Showing <span className="font-semibold text-foreground">{totalResults}</span> {totalResults === 1 ? "listing" : "listings"}
        </div>
      )}
    </div>
  );
}
