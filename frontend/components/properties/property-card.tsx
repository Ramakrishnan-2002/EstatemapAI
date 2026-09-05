import React from "react";
import Link from "next/link";
import { Building2, Heart, Scale } from "lucide-react";
import { Property } from "@/types";
import { LocationDisplay } from "@/components/properties/location-display";
import { PriceDisplay } from "@/components/properties/price-display";
import { PropertyMeta } from "@/components/properties/property-meta";
import { Badge } from "@/components/ui/badge";
import { formatPropertyType } from "@/lib/formatters/property";
import { cn } from "@/lib/utils";
import { useComparison } from "@/context/comparison-context";

interface PropertyCardProps {
  property: Property;
  className?: string;
  isSaved?: boolean;
  isSelected?: boolean;
  isHovered?: boolean;
  onSelect?: (property: Property) => void;
  onMouseEnter?: (property: Property) => void;
  onMouseLeave?: (property: Property) => void;
  onToggleSave?: (propertyId: number, e: React.MouseEvent) => void;
}

export function PropertyCard({
  property,
  className,
  isSaved = false,
  isSelected = false,
  isHovered = false,
  onSelect,
  onMouseEnter,
  onMouseLeave,
  onToggleSave,
}: PropertyCardProps) {
  const { toggleCompare, isCompared } = useComparison();
  const compared = isCompared(property.id);

  const primaryImage =
    property.images && property.images.length > 0
      ? property.images[0].image_url
      : null;

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

        {/* Top Badges Overlay */}
        <div className="absolute left-2.5 top-2.5 flex items-center gap-1.5">
          <Badge variant="secondary" className="bg-background/90 text-xs font-medium backdrop-blur-sm shadow-sm">
            {formatPropertyType(property.property_type)}
          </Badge>
          {property.status && property.status !== "active" && (
            <Badge variant="warning" className="text-xs font-medium shadow-sm">
              {property.status.toUpperCase()}
            </Badge>
          )}
        </div>

        {/* Compare Toggle and Save Action Overlay */}
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
