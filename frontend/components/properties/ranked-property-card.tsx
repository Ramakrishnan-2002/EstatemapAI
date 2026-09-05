"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Building2, Heart, Sparkles, ChevronDown, ChevronUp, CheckCircle, Info, Scale } from "lucide-react";
import { RankedPropertyItem } from "@/types";
import { LocationDisplay } from "@/components/properties/location-display";
import { PriceDisplay } from "@/components/properties/price-display";
import { PropertyMeta } from "@/components/properties/property-meta";
import { Badge } from "@/components/ui/badge";
import { formatPropertyType } from "@/lib/formatters/property";
import { cn } from "@/lib/utils";
import { useComparison } from "@/context/comparison-context";

interface RankedPropertyCardProps {
  item: RankedPropertyItem;
  className?: string;
  isSaved?: boolean;
  isSelected?: boolean;
  isHovered?: boolean;
  onSelect?: (property: RankedPropertyItem["property"]) => void;
  onMouseEnter?: (property: RankedPropertyItem["property"]) => void;
  onMouseLeave?: (property: RankedPropertyItem["property"]) => void;
  onToggleSave?: (propertyId: number, e: React.MouseEvent) => void;
}

const FACTOR_LABELS: Record<string, string> = {
  price: "Price Match",
  bedrooms: "Bedrooms",
  area: "Living Area",
  locality: "Locality",
  location: "Nearby POIs",
  commute: "Commute",
};

export function RankedPropertyCard({
  item,
  className,
  isSaved = false,
  isSelected = false,
  isHovered = false,
  onSelect,
  onMouseEnter,
  onMouseLeave,
  onToggleSave,
}: RankedPropertyCardProps) {
  const { toggleCompare, isCompared } = useComparison();
  const [showDetails, setShowDetails] = useState<boolean>(false);
  const { property, rank, final_score, score_breakdown, explanations } = item;
  const compared = isCompared(property.id);

  const primaryImage =
    property.images && property.images.length > 0
      ? property.images[0].image_url
      : null;

  // Rank badge styling
  const getRankBadgeStyle = (r: number) => {
    if (r === 1) return "bg-amber-500/15 text-amber-600 dark:text-amber-400 border-amber-500/30 font-bold";
    if (r === 2) return "bg-slate-500/15 text-slate-700 dark:text-slate-300 border-slate-500/30 font-semibold";
    if (r === 3) return "bg-orange-500/15 text-orange-600 dark:text-orange-400 border-orange-500/30 font-semibold";
    return "bg-muted text-muted-foreground border-border font-medium";
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-emerald-600 dark:text-emerald-400";
    if (score >= 60) return "text-primary";
    return "text-muted-foreground";
  };

  return (
    <div
      id={`property-card-${property.id}`}
      onClick={() => onSelect?.(property)}
      onMouseEnter={() => onMouseEnter?.(property)}
      onMouseLeave={() => onMouseLeave?.(property)}
      className={cn(
        "group relative flex flex-col overflow-hidden rounded-lg border bg-card shadow-xs transition-all duration-200 cursor-pointer",
        isSelected
          ? "border-emerald-500 ring-2 ring-emerald-500/30 shadow-md bg-emerald-500/5"
          : isHovered
          ? "border-primary/60 shadow-md"
          : "border-border hover:border-primary/40 hover:shadow-md",
        className
      )}
    >
      {/* Property Image Container */}
      <Link href={`/properties/${property.id}`} className="relative aspect-[16/10] w-full overflow-hidden bg-muted">
        {primaryImage ? (
          <img
            src={primaryImage}
            alt={property.title}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="flex h-full w-full flex-col items-center justify-center bg-muted/60 text-muted-foreground">
            <Building2 className="h-10 w-10 stroke-[1.25] text-muted-foreground/60" />
            <span className="mt-1 text-xs font-medium">EstateMap Listing</span>
          </div>
        )}

        {/* Top Rank & Type Badges */}
        <div className="absolute left-2.5 top-2.5 flex items-center gap-1.5 flex-wrap">
          <Badge
            variant="outline"
            className={cn("text-xs shadow-xs backdrop-blur-sm px-2 py-0.5 border", getRankBadgeStyle(rank))}
          >
            #{rank} Match
          </Badge>
          <Badge variant="secondary" className="bg-background/90 text-xs font-medium backdrop-blur-sm shadow-sm">
            {formatPropertyType(property.property_type)}
          </Badge>
        </div>

        {/* Overall Match Score Floating Badge & Actions */}
        <div className="absolute right-2.5 top-2.5 flex items-center gap-1.5">
          <button
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              toggleCompare(property);
            }}
            className={cn(
              "flex h-7 items-center gap-1 px-2 rounded-full backdrop-blur-sm text-[11px] font-semibold transition-all shadow-xs",
              compared
                ? "bg-primary text-primary-foreground ring-2 ring-primary/40"
                : "bg-background/80 text-foreground hover:bg-background hover:text-primary"
            )}
            aria-label="Compare property"
          >
            <Scale className="h-3 w-3" />
            <span>{compared ? "Comparing" : "Compare"}</span>
          </button>

          <div className="flex items-center gap-1 rounded-md bg-background/90 px-2 py-1 shadow-sm backdrop-blur-sm border border-border">
            <Sparkles className="h-3 w-3 text-emerald-500" />
            <span className={cn("text-xs font-bold font-mono", getScoreColor(final_score))}>
              {final_score.toFixed(1)}%
            </span>
          </div>

          {/* Favorite Action */}
          {onToggleSave && (
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault();
                e.stopPropagation();
                onToggleSave(property.id, e);
              }}
              className="flex h-7 w-7 items-center justify-center rounded-full bg-background/80 text-foreground backdrop-blur-sm transition-colors hover:bg-background hover:text-destructive"
              aria-label="Save property"
            >
              <Heart
                className={cn("h-3.5 w-3.5", isSaved && "fill-destructive text-destructive")}
              />
            </button>
          )}
        </div>
      </Link>

      {/* Card Content */}
      <div className="flex flex-1 flex-col p-4">
        {/* Price Row */}
        <div className="flex items-baseline justify-between">
          <PriceDisplay
            price={property.price}
            areaSqFt={property.area_sqft}
            size="md"
            showRate
          />
        </div>

        {/* Title */}
        <Link
          href={`/properties/${property.id}`}
          className="mt-1.5 font-medium text-foreground transition-colors hover:text-primary line-clamp-1"
          title={property.title}
        >
          {property.title}
        </Link>

        {/* Location Display */}
        <LocationDisplay
          locality={property.locality}
          city={property.city}
          className="mt-1.5"
        />

        {/* Factor Breakdown Compact Bars */}
        <div className="mt-3 rounded-md bg-muted/40 p-2 border border-border/50 space-y-1.5 text-xs">
          <div className="flex items-center justify-between text-[11px] font-medium text-muted-foreground">
            <span className="flex items-center gap-1">
              <Info className="h-3 w-3 text-primary" />
              Scoring Factors
            </span>
            <button
              type="button"
              onClick={(e) => {
                e.stopPropagation();
                setShowDetails(!showDetails);
              }}
              className="flex items-center gap-0.5 text-[11px] font-semibold text-primary hover:underline"
            >
              {showDetails ? (
                <>
                  <span>Less</span>
                  <ChevronUp className="h-3 w-3" />
                </>
              ) : (
                <>
                  <span>Why this rank?</span>
                  <ChevronDown className="h-3 w-3" />
                </>
              )}
            </button>
          </div>

          {/* Mini progress bars for top available factors */}
          <div className="grid grid-cols-2 gap-x-3 gap-y-1.5 pt-0.5">
            {Object.entries(score_breakdown).map(([factor, detail]) => {
              if (!detail.available) return null;
              const percent = Math.round(detail.score * 100);
              return (
                <div key={factor} className="space-y-0.5">
                  <div className="flex items-center justify-between text-[10px] text-muted-foreground">
                    <span>{FACTOR_LABELS[factor] || factor}</span>
                    <span className="font-mono font-medium">{percent}%</span>
                  </div>
                  <div className="h-1.5 w-full overflow-hidden rounded-full bg-muted">
                    <div
                      className="h-full rounded-full bg-emerald-500 transition-all duration-300"
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          {/* Expandable Explanation Bullet Points */}
          {showDetails && explanations && explanations.length > 0 && (
            <div className="mt-2.5 pt-2 border-t border-border/60 space-y-1">
              <span className="text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
                Match Highlights
              </span>
              <ul className="space-y-1 text-[11px] text-foreground/90">
                {explanations.map((exp, idx) => (
                  <li key={idx} className="flex items-start gap-1.5">
                    <CheckCircle className="h-3 w-3 text-emerald-600 mt-0.5 shrink-0" />
                    <span>{exp}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Specifications Meta */}
        <div className="mt-auto pt-3 border-t border-border/60">
          <PropertyMeta
            bedrooms={property.bedrooms}
            bathrooms={property.bathrooms}
            areaSqFt={property.area_sqft}
          />
        </div>
      </div>
    </div>
  );
}
